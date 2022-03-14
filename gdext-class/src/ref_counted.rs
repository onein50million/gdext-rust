use std::ffi::{CString};
use std::ptr::null;
use once_cell::sync::Lazy;
use gdext_sys::{self as sys, get_interface};
use crate::GodotClass;

pub struct RefCounted(sys::GDNativeObjectPtr);

impl GodotClass for RefCounted {
    type Base = RefCounted;

    fn class_name() -> String {
        "RefCounted".to_string()
    }

    fn native_object_ptr(&self) -> sys::GDNativeObjectPtr {
        self.0
    }

    fn upcast(&self) -> &Self::Base {
        self
    }

    fn upcast_mut(&mut self) -> &mut Self::Base {
        self
    }

}



impl Clone for RefCounted{
    fn clone(&self) -> Self {
        unsafe{
            let ref_counted = CString::new("RefCounted").unwrap();
            let reference = CString::new("reference").unwrap();
            let method_bind = get_interface().classdb_get_method_bind.unwrap()(
                ref_counted.as_ptr(),
                reference.as_ptr(),
                135338150
            );

            let mut return_value = 0;

            get_interface().object_method_bind_ptrcall.unwrap()(
                method_bind,self.0 , null(), &mut return_value as *mut _ as *mut _
            );
            Self(self.0)
        }
    }
}

impl Drop for RefCounted{
    fn drop(&mut self) {
        unsafe{
            let ref_counted = CString::new("RefCounted").unwrap();
            let unreference = CString::new("unreference").unwrap();
            let method_bind = get_interface().classdb_get_method_bind.unwrap()(
                ref_counted.as_ptr(),
                unreference.as_ptr(),
                135338150
            );

            let mut return_value = 0;

            get_interface().object_method_bind_ptrcall.unwrap()(
                method_bind,self.0 , null(), &mut return_value as *mut _ as *mut _
            );
        }
    }
}