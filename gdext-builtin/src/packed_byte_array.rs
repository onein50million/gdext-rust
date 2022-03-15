use std::{ffi::{CString}, mem::MaybeUninit};

use once_cell::sync::Lazy;
use gdext_sys::{self as sys, interface_fn};
use crate::PtrCallArg;

#[repr(C, align(8))]
#[derive(Clone, Debug)]
pub struct PackedByteArray(MaybeUninit<[u8; 16 as usize]>);

impl PackedByteArray{
    #[doc(hidden)]
    pub fn as_mut_ptr(&mut self) -> sys::GDNativeObjectPtr {
        self.0.as_mut_ptr() as *mut _
    }
    #[doc(hidden)]
    pub fn as_ptr(&self) -> sys::GDNativeObjectPtr {
        self.0.as_ptr() as *mut _
    }

    pub fn new() -> Self {
        unsafe {
            let mut byte_array = Self(MaybeUninit::uninit());

            static CONSTR: Lazy<
                unsafe extern "C" fn(sys::GDNativeTypePtr, *const sys::GDNativeTypePtr),
            > = Lazy::new(|| unsafe {
                interface_fn!(variant_get_ptr_constructor)(
                    sys::GDNativeVariantType_GDNATIVE_VARIANT_TYPE_PACKED_BYTE_ARRAY,
                    0,
                )
                    .unwrap()
            });
            CONSTR(byte_array.as_mut_ptr(), std::ptr::null());
            byte_array
        }
    }
    pub fn resize(&mut self, value: u8){
        unsafe{
            let args = [value];
            let p_args = args.as_ptr();
            let resize_str = CString::new("resize").unwrap();
            let resize_fn = sys::get_interface().variant_get_ptr_builtin_method.unwrap()(sys::GDNativeVariantType_GDNATIVE_VARIANT_TYPE_PACKED_BYTE_ARRAY, resize_str.as_ptr(), 2).unwrap();
            let mut return_value = 0;
            resize_fn(self.as_mut_ptr(), &p_args as *const _ as _,&mut return_value as *mut _ as _, 1);
        }
    } 
    pub fn append(&mut self, value: u8){
        unsafe{
            let args = [value];
            let p_args = args.as_ptr();
            let append_str = CString::new("append").unwrap();
            let append_fn = sys::get_interface().variant_get_ptr_builtin_method.unwrap()(sys::GDNativeVariantType_GDNATIVE_VARIANT_TYPE_PACKED_BYTE_ARRAY, append_str.as_ptr(), 2).unwrap();
            let mut return_value = 0;
            append_fn(self.as_mut_ptr(), &p_args as *const _ as _,&mut return_value as *mut _ as _, 1);
        }
    }

    pub fn size(&self) -> u32{
        unsafe{
            let size_str = CString::new("size").unwrap();
            let size_fn = sys::get_interface().variant_get_ptr_builtin_method.unwrap()(sys::GDNativeVariantType_GDNATIVE_VARIANT_TYPE_PACKED_BYTE_ARRAY, size_str.as_ptr(), 171192809).unwrap();
            let mut return_value = 0;
            size_fn(self.as_ptr(), std::ptr::null(), &mut return_value as *mut _ as _, 0);
            return_value
        }
    }
}

impl Default for PackedByteArray {
    fn default() -> Self {
        Self::new()
    }
}

impl Drop for PackedByteArray {
    fn drop(&mut self) {
        unsafe {
            static DESTR: Lazy<unsafe extern "C" fn(sys::GDNativeTypePtr)> = Lazy::new(|| unsafe {
                interface_fn!(variant_get_ptr_destructor)(
                    sys::GDNativeVariantType_GDNATIVE_VARIANT_TYPE_PACKED_BYTE_ARRAY,
                )
                    .unwrap()
            });
            DESTR(self.as_mut_ptr());
        }
    }
}

impl PtrCallArg for PackedByteArray{
    unsafe fn from_ptr_call_arg(arg: *const gdext_sys::GDNativeTypePtr) -> Self {
        Clone::clone(&*(arg as *mut PackedByteArray))
    }

    unsafe fn to_ptr_call_arg(self, arg: gdext_sys::GDNativeTypePtr) {
        std::ptr::write(arg as *mut PackedByteArray, self);
    }
}
