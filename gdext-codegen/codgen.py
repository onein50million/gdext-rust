import json
import os
import re
import shutil

#🐟

desired_build_config = "double_64"


def get_builtin_class_size(api, builtin_class: str) -> int:
    for build_config in api["builtin_class_sizes"]:
        if build_config["build_configuration"] == desired_build_config:
            for size in build_config["sizes"]:
                if size["name"] == builtin_class:
                    return size["size"]


def write_string_and_make_dirs(file_path: str, to_write: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(to_write)


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.replace("2_D", "2D").replace("3_D", "3D").lower()

def cleanup_type(type_string: str, class_name = "", only_include_last = True) -> str:
    out_string = type_string
    if "enum::" in out_string:
        out_string = re.sub(r"enum::", '', out_string)
        if class_name != "":
            out_string = re.sub(fr"{class_name}\.", '', out_string)
        out_string = re.sub(r"\.", '::', out_string)
    if only_include_last:
        out_string = re.sub(r".+(?<=::)", '', out_string)
    return out_string

def try_add_import(import_set: set, import_name):
    if "enum::" not in import_name:
        import_set.add((import_name, import_name))
    else:
        new_import_name = re.sub(r"enum::", '', import_name)
        import_set.add(tuple(new_import_name.split('.')))
api_filepath = "../thirdparty/godot-headers/extension_api.json"

shutil.rmtree("src/gen")

write_string_and_make_dirs(f"src/gen/mod.rs", "//generated file\npub mod global_enums;\n")

header = """
#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(unused_imports)]
#![allow(dead_code)]
"""

global_enums = set()

# bitfield_enums = (
#     "InlineAlignment",
#     "InlineAlignment",
#     "KeyModifierMask"
# )

with open(api_filepath, "r") as api_file:
    data = api_file.read()
    data = re.sub("bool", "GDBool", data)
    api = json.loads(data)

    enum_file = "" + header
    enum_file += "use bitflags::bitflags;\n"
    for enum in api["global_enums"]:
        enum_name = enum["name"]
        split = False
        if "." in enum_name:
            split = True
            enum_split = enum_name.split(".")
            enum_name = enum_split[1]
            enum_module = enum_split[0]
        global_enums.add(enum_name)
        enum_file += f"bitflags!{{\n#[repr(C)]\npub struct {enum_name}:i64{{"
        for value in enum["values"]:
            enum_file += f"const {value['name']} = {value['value']};\n"
        enum_file += "}}\n"
    write_string_and_make_dirs("src/gen/global_enums.rs", enum_file)
    for builtin_class in api["builtin_classes"]:

        out_class = "//Generated file, edits will be lost\n"
        use_block = """
        use std::{ffi::{CString}, mem::MaybeUninit, ops::{Index, IndexMut}};
        use once_cell::sync::Lazy;
        use gdext_sys::{self as sys, interface_fn};
        use gdext_builtin::{PtrCallArg};
        use gdext_builtin::variant::Variant;
        use crate::gen::global_enums::*;
        use bitflags::bitflags;
        """

        required_imports = set()
        class_name = builtin_class['name']

        method_block = ""
        if class_name == "Vector3":
            method_block += """
            bitflags! {
            #[repr(C)]
            pub struct Axis:i64{
            }
            }
            """

        class_size = get_builtin_class_size(api, class_name)
        method_block += f"""
        #[repr(C)]
        #[derive(Debug)]
        pub struct {class_name} (pub MaybeUninit<[u8; {class_size}]>);\n"""

        # method_block += f"""
        #     impl GodotClass for RefCounted {{
        #     type Base = {class_name};

        #     fn class_name() -> String {{
        #         "{class_name}".to_string()
        #     }}

        #     fn native_object_ptr(&self) -> sys::GDNativeObjectPtr {{
        #         self.0
        #     }}

        #     fn upcast(&self) -> &Self::Base {{
        #         self
        #     }}

        #     fn upcast_mut(&mut self) -> &mut Self::Base {{
        #         self
        #     }}

        # }}
        
        
        # """

        method_block += f"impl {class_name}{{\n"
        
        method_block += f"""
        pub fn get_mut_ptr(&mut self) -> sys::GDNativeObjectPtr{{
            self.0.as_mut_ptr() as *mut _
        }}
        """

        if "methods" in builtin_class:
            for method in builtin_class["methods"]:
                method_hash = method["hash"]
                return_string = ""
                if "return_type" in method:
                    try_add_import(required_imports, method['return_type'])
                    return_string += "-> "
                    return_string += method["return_type"]
                argument_string = "&mut self, "
                arg_array_string = "["
                arg_count = 0
                if "arguments" in method:
                    arg_count = len(method["arguments"])
                    for argument in method["arguments"]:
                        try_add_import(required_imports, argument['type'])
                        argument_string += f"r#{argument['name']}: &mut r#{argument['type']}, "
                        arg_array_string += f"r#{argument['name']} as *mut _ as _, "
                arg_array_string += "]"
                method_block += f"""
                pub fn r#{method["name"]} ({argument_string}){return_string}{{
                    unsafe{{
                    let args = {arg_array_string};
                    let p_args = args.as_ptr();
                    let method_str = CString::new("{method['name']}").unwrap();
                    let method_fn = sys::get_interface().variant_get_ptr_builtin_method.unwrap()(sys::GDNativeVariantType_GDNATIVE_VARIANT_TYPE_{camel_to_snake(class_name).upper()}, method_str.as_ptr(), {method_hash}).unwrap();
                    let mut return_value = MaybeUninit::uninit();
                    method_fn(self.0.as_mut_ptr() as *mut _, p_args,return_value.as_mut_ptr() as _, {arg_count});
                    return_value.assume_init()
                    }}
                }}
                """
        method_block += "}\n"

        for import_name_tuple in required_imports:
            if class_name in import_name_tuple:
                continue
            if "Variant" in import_name_tuple:
                continue
            use_block += f"use crate::gen::r#{'::r#'.join(import_name_tuple)};\n"
        out_class += header
        out_class += use_block
        out_class += method_block
        write_string_and_make_dirs(f"src/gen/{class_name}.rs", out_class)
        with open("src/gen/mod.rs", "a") as lib_file:
            lib_file.write(f"pub mod {class_name};")
    
    #Non builtin classes
    for regular_class in api["classes"]:
        out_class = "//Generated file, edits will be lost\n"
        use_block = """
        use std::{ffi::{CString}, mem::MaybeUninit, ops::{Index, IndexMut}};
        use once_cell::sync::Lazy;
        use gdext_sys::{self as sys, interface_fn};
        use gdext_builtin::{PtrCallArg};
        use gdext_builtin::variant::Variant;
        use crate::gen::global_enums::*;
        use bitflags::bitflags;
        """

        enum_block = ""
        if "enums" in regular_class:
            for enum in regular_class["enums"]:
                enum_name = enum["name"]
                split = False
                if "." in enum_name:
                    split = True
                    enum_split = enum_name.split(".")
                    enum_name = enum_split[1]
                    enum_module = enum_split[0]
                enum_block += f"bitflags!{{\n#[repr(C)]\npub struct {enum_name}:i64{{"
                for value in enum["values"]:
                    enum_block += f"const {value['name']} = {value['value']};\n"
                enum_block += "}}\n"


        required_imports = set()
        class_name = regular_class['name']
        inherited_class_name = ""
        #Object doesn't inherit anything
        if class_name == "Object":
            method_block = f"""
            #[repr(C)]
            #[derive(Debug)]
            pub struct {class_name} {{
                pub ptr: MaybeUninit<[u8;8]>
            }}\n
            """
        else:
            try_add_import(required_imports,regular_class['inherits'])
            inherited_class_name = regular_class['inherits']
            method_block = f"""
            #[repr(C)]
            #[derive(Debug)]
            pub struct r#{class_name} {{
                pub base: {regular_class['inherits']},
                pub ptr: MaybeUninit<[u8;8]>
            }}\n
            """
        method_block += f"impl {class_name}{{\n"
        

        method_block += f"""
        pub fn get_mut_ptr(&mut self) -> sys::GDNativeObjectPtr{{
            self.ptr.as_mut_ptr() as *mut _
        }}
        """

        if inherited_class_name != "":
            method_block += f"""
            pub fn new () -> {class_name}{{
                unsafe{{
                    let mut new_object = Self{{
                        base: {inherited_class_name}::new(),
                        ptr: MaybeUninit::uninit()
                    }};
                    let class_str = CString::new("{class_name}").unwrap();
                    new_object.ptr.write((sys::get_interface().classdb_construct_object.unwrap()(class_str.as_ptr()) as usize).to_ne_bytes());
                    let inherited_str = CString::new("{inherited_class_name}").unwrap();
                    sys::get_interface().object_set_instance.unwrap()(new_object.get_mut_ptr(), inherited_str.as_ptr(), new_object.base.get_mut_ptr());
                    new_object
                }}
            }}
            """
        else:
            method_block += f"""
            pub fn new () -> {class_name}{{
                unsafe{{
                    let class_str = CString::new("{class_name}").unwrap();
                    let object = sys::get_interface().classdb_construct_object.unwrap()(class_str.as_ptr());
                    Self{{
                        ptr: MaybeUninit::new((object as usize).to_ne_bytes())
                    }}
                }}
            }}
            """



        if "methods" in regular_class:
            for method in regular_class["methods"]:
                if method['name'] == "new":
                    continue
                if method["is_virtual"]:
                    continue
                method_hash = method["hash"]
                return_string = ""
                has_return = False
                if "return_value" in method and method['return_value']["type"] != "void":
                    has_return = True
                    try_add_import(required_imports, method['return_value']["type"])
                    return_string += "-> "
                    return_string += cleanup_type(method['return_value']["type"], class_name)
                argument_string = "&mut self, "
                arg_array_string = "["
                arg_count = 0
                if "arguments" in method:
                    arg_count = len(method["arguments"])
                    for argument in method["arguments"]:
                        try_add_import(required_imports, argument['type'])
                        argument_string += f"r#{argument['name']}: &mut r#{cleanup_type(argument['type'], class_name)}, "
                        arg_array_string += f"r#{argument['name']} as *mut _ as _, "
                arg_array_string += "]"
                return_value_string = ""
                if has_return:
                    return_value_string = "std::ptr::read(return_value.as_mut_ptr() as *mut _)"
                method_block += f"""
                pub fn r#{method["name"]} ({argument_string}){return_string}{{
                    unsafe{{
                    let args = {arg_array_string};
                    let p_args = args.as_ptr();
                    let method_str = CString::new("{method['name']}").unwrap();
                    let class_str = CString::new("{class_name}").unwrap();
                    let method_fn = sys::get_interface().classdb_get_method_bind.unwrap()(class_str.as_ptr(), method_str.as_ptr(), {method_hash});
                    let mut return_value = MaybeUninit::uninit();
                    sys::get_interface().object_method_bind_ptrcall.unwrap()(method_fn,self.get_mut_ptr(),p_args, return_value.as_mut_ptr());
                    {return_value_string}
                    }}
                }}
                """
        method_block += "}\n"

        for import_name_tuple in required_imports:
            if class_name in import_name_tuple:
                continue
            if "Variant" in import_name_tuple:
                continue
            should_do_continue = False
            for import_name in import_name_tuple:
                if import_name in global_enums:
                    should_do_continue = True
                    break
            if should_do_continue == True:
                continue
            use_block += f"use crate::gen::r#{'::r#'.join(import_name_tuple)};\n"
        out_class += header
        out_class += use_block
        out_class += enum_block
        out_class += method_block
        write_string_and_make_dirs(f"src/gen/{class_name}.rs", out_class)
        with open("src/gen/mod.rs", "a") as lib_file:
            lib_file.write(f"pub mod {class_name};")
print("running cargo fmt")
os.system("cargo fmt")
print("cargo fmt done")
# print("running cargo fix")
# os.system("cargo fix --allow-dirty")
# print("cargo fix done")