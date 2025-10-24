import os
from PIL import Image
import numpy as np
import torch
import folder_paths

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

ANY = AnyType("*")

class LOCK_TOGGLE:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": (ANY,),
            }
        }

    RETURN_TYPES = (ANY,)
    FUNCTION = "passthrough"
    CATEGORY = "utils/Lock Nodes"

    def passthrough(self, input):
        return (input,)


class LOCK_IMAGE:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "image": ("IMAGE",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "lock_image"
    CATEGORY = "utils/Lock Nodes"
    
    def tensor2pil(self, image):
        return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))
    
    def pil2tensor(self, image):
        return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)
    
    @classmethod
    def get_temp_image_file_path(cls, workflow_id, unique_id, image_type):
        """Generate a temporary file path for the image based on the unique ID."""
        workflow_image_dir = os.path.join(folder_paths.get_output_directory(), "__lock_files", workflow_id)
        if not os.path.exists(workflow_image_dir):
            os.makedirs(workflow_image_dir)
        return os.path.join(workflow_image_dir, f"locked_{image_type}_{unique_id}.png")
    
    @classmethod
    def get_workflow_id_from_extra_pnginfo(cls, extra_pnginfo):
        """Extract the workflow ID from the extra PNG info."""
        return extra_pnginfo.get("workflow", dict()).get("id", "__no_workflow")

    def lock_image(self, image=None, unique_id=None, extra_pnginfo=None, image_type="image"):
        if extra_pnginfo is None:
            raise Exception("extra_pnginfo must be provided to lock the image.")
        temp_image_path = LOCK_IMAGE.get_temp_image_file_path(LOCK_IMAGE.get_workflow_id_from_extra_pnginfo(extra_pnginfo), unique_id, image_type)

        if image != None:
            pil_image = self.tensor2pil(image)
            pil_image.save(temp_image_path)
            return (image,)
        
        if not os.path.exists(temp_image_path):
            raise Exception("No image to lock, please send an image into this node at least once.")
        
        pil_image = Image.open(temp_image_path)
        return (self.pil2tensor(pil_image),)

class LOCK_MASK(LOCK_IMAGE):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "mask": ("MASK",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }
    
    RETURN_TYPES = ("MASK",)
    FUNCTION = "lock_mask"
    CATEGORY = "utils/Lock Nodes"

    def lock_mask(self, mask=None, unique_id=None, extra_pnginfo=None):
        return super().lock_image(image=mask, unique_id=unique_id, extra_pnginfo=extra_pnginfo, image_type="mask")

NODE_CLASS_MAPPINGS = {
    "Lock Image": LOCK_IMAGE,
    "Lock Mask": LOCK_MASK,
    "Lock Toggle": LOCK_TOGGLE,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Lock Image": "🔒 Lock Image",
    "Lock Mask": "🔒 Lock Mask",
    "Lock Toggle": "🔒 Toggle"
}
