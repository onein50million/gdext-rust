use std::ptr::null_mut;

use once_cell::sync::Lazy;
use gdext_sys::{self as sys, interface_fn};
use crate::PtrCallArg;

#[repr(C, align(8))]
#[derive(Clone, Debug)]
pub struct PackedByteArray{
    gd_native_ptr: sys::GDNativeTypePtr,
    pub vec: Vec<u8>
}

impl PackedByteArray{
    #[doc(hidden)]
    pub fn as_mut_ptr(&mut self) -> sys::GDNativeObjectPtr {
        self.gd_native_ptr
    }
    #[doc(hidden)]
    pub fn as_ptr(&self) -> sys::GDNativeObjectPtr {
        self.gd_native_ptr
    }

    pub fn new() -> Self {
        unsafe {
            let mut byte_array = Self{
                gd_native_ptr: null_mut(),
                vec: vec![],
            };

            static CONSTR: Lazy<
                unsafe extern "C" fn(sys::GDNativeTypePtr, *const sys::GDNativeTypePtr),
            > = Lazy::new(|| unsafe {
                interface_fn!(variant_get_ptr_constructor)(
                    sys::GDNativeVariantType_GDNATIVE_VARIANT_TYPE_PACKED_BYTE_ARRAY,
                    0,
                )
                    .unwrap()
            });
            let vec: sys::GDNativeTypePtr = byte_array.vec.as_mut_ptr() as _;
            CONSTR(byte_array.as_mut_ptr(), &vec as _);
            byte_array
        }
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
