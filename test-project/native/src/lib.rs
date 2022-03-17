use std::mem::MaybeUninit;

use gdext_builtin::{
    gdext_init, string::GodotString, variant::Variant, InitLevel,
};
use gdext_sys::{self as sys};

use gdext_codegen::gen::Node3D::Node3D;
use gdext_codegen::gen::Vector3::Vector3;

// pub struct RustTest {
//     base: Node3D,
//     time: f64,
// }

// impl GodotClass for RustTest {
//     type Base = Node3D;

//     fn class_name() -> String {
//         "RustTest".to_string()
//     }

//     fn upcast(&self) -> &Self::Base {
//         &self.base
//     }

//     fn upcast_mut(&mut self) -> &mut Self::Base {
//         &mut self.base
//     }
// }

// impl GodotExtensionClass for RustTest {
//     fn construct(base: sys::GDNativeObjectPtr) -> Self {
//         RustTest {
//             base: Node3D::new(),
//             time: 0.0,
//         }
//     }
// }

// impl RustTest {
//     fn test_method(&mut self, some_int: u64, some_string: GodotString) -> GodotString {
//         let msg = format!("Hello from `RustTest.test_method()`, you passed some_int={some_int} and some_string={some_string}");
//         msg.into()
//     }

//     fn add(&self, a: i32, b: i32, c: Vector2) -> i64 {
//         a as i64 + b as i64 + c.length() as i64
//     }

//     fn vec_add(&self, a: Vector2, b: Vector2) -> Vector2 {
//         a + b
//     }

//     fn _ready(&mut self) {
//         gdext_print_warning!("Hello from _ready()!");
//     }

//     fn _process(&mut self, delta: f64) {
//         let mod_before = self.time % 1.0;
//         self.time += delta;
//         let mod_after = self.time % 1.0;

//         if mod_before > mod_after {
//             eprintln!("Boop! {}", self.time);
//         }
//     }
// }

// impl GodotExtensionClassMethods for RustTest {
//     fn virtual_call(name: &str) -> sys::GDNativeExtensionClassCallVirtual {
//         match name {
//             "_ready" => gdext_virtual_method_body!(RustTest, fn _ready(&mut self)),
//             "_process" => gdext_virtual_method_body!(RustTest, fn _process(&mut self, delta: f64)),
//             _ => None,
//         }
//     }

//     fn register_methods() {
//         gdext_wrap_method!(RustTest,
//             fn test_method(&mut self, some_int: u64, some_string: GodotString) -> GodotString
//         );

//         gdext_wrap_method!(RustTest,
//             fn add(&self, a: i32, b: i32, c: Vector2) -> i64
//         );

//         gdext_wrap_method!(RustTest,
//             fn vec_add(&self, a: Vector2, b: Vector2) -> Vector2
//         );
//     }
// }

gdext_init!(gdext_rust_test, |init: &mut gdext_builtin::InitOptions| {
    init.register_init_function(InitLevel::Scene, || {
        // register_class::<RustTest>();

        variant_tests();
        node3D_tests();

    });
});

fn node3D_tests(){
    let mut node = Node3D::new();
    unsafe{
        dbg!(f64::from_ne_bytes(node.get_position().0.assume_init()[..8].try_into().unwrap()));
        dbg!(f64::from_ne_bytes(node.get_position().0.assume_init()[8..][..8].try_into().unwrap()));
        dbg!(f64::from_ne_bytes(node.get_position().0.assume_init()[16..][..8].try_into().unwrap()));
    }
    let mut new_position = Vector3(MaybeUninit::new([
        124;24
    ]));

    unsafe{
        dbg!(f64::from_ne_bytes(new_position.0.assume_init()[8..][..8].try_into().unwrap()));
        dbg!(f64::from_ne_bytes(new_position.0.assume_init()[..8].try_into().unwrap()));
        dbg!(f64::from_ne_bytes(new_position.0.assume_init()[16..][..8].try_into().unwrap()));
    }


    node.set_position(&mut new_position);
    unsafe{
        dbg!(f64::from_ne_bytes(node.get_position().0.assume_init()[..8].try_into().unwrap()));
    }

}

fn variant_tests() {
}
