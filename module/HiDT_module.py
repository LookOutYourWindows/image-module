import os, io
from re import S
from numpy import source
import torch, boto3, yaml

from torchvision import transforms
from PIL import Image
from typing import List

from hidt.style_transformer import StyleTransformer
from hidt.preprocessing import GridCrop, enhancement_preprocessing
from utils import remove_ext

BUCKET_NAME = "loyw"
MODEL_DIR = "../data/models/"

s3 = boto3.client('s3')

class HiDT_module:

    checkpoint_file = None
    g_enh = None
    config_file = None

    @classmethod
    def get_model(cls):
        """
        Get the model object for this instance, loading it if it's not already loaded.
        """
        if cls.checkpoint_file is None:
            cls.checkpoint_file = torch.load(os.path.join(MODEL_DIR, "daytime.pt"), map_location=torch.device('cpu'))

        if cls.g_enh is None:
            cls.g_enh = torch.jit.load(os.path.join(MODEL_DIR, "enhancer.pt")).eval()

        if cls.config_file is None:
            cls.config_file = yaml.load(open(os.path.join(MODEL_DIR, "daytime.yaml"), 'r'), Loader=yaml.SafeLoader)
        
        return cls.checkpoint_file, cls.g_enh, cls.config_file


    @classmethod
    def infer(cls,
              username: str,
              source_image: str, 
              style_dir: str) -> List[str]:

        checkpoint_file, g_enh, config_file = cls.get_model()
        
        response = s3.get_object(
            Bucket=BUCKET_NAME, 
            Key=username + "/" + source_image,
        )

        source_images_pil = [Image.open(response["Body"])]
        inference_size = min(source_images_pil[0].size) // 4

        output_bytes = io.BytesIO()
        thumbnail = source_images_pil[0].copy()
        thumbnail.thumbnail((401, 291), Image.ANTIALIAS)
        thumbnail.save(output_bytes, "JPEG")
        source_image_name = remove_ext(source_image)
        output_name = source_image_name + "_" + "thumbnail.jpg"
        
        response = s3.put_object(
            Body=output_bytes.getvalue(), 
            Bucket=BUCKET_NAME, 
            Key=username + "/" + source_image_name +"/" + output_name
        )

    
        style_images = os.listdir(style_dir)
        style_images_name = [path[path.rfind('/') + 1:] for path in style_images]
        style_images_pil = [Image.open(os.path.join(style_dir, style_image)).convert('RGB') for style_image in style_images]
        style_transformer = StyleTransformer(config_file, checkpoint_file,
                                            inference_size=inference_size,
                                            device='cpu')

        with torch.no_grad():
            crop_transform = GridCrop(4, 1, hires_size=inference_size * 4)

            result_images = []
            for i, style_img_pil in enumerate(style_images_pil): 
                styles_decomposition = style_transformer.get_style([style_img_pil])
                crops = [img for img in crop_transform(source_images_pil[0])]
                out = style_transformer.transfer_images_to_styles(crops, styles_decomposition, batch_size=1, return_pil=False)
                padded_stack = enhancement_preprocessing(out[0])
                out = g_enh(padded_stack)
                output_img = transforms.ToPILImage()((out[0].cpu().clamp(-1, 1) + 1.) / 2.)
                
                output_bytes = io.BytesIO()
                output_img.save(output_bytes, "JPEG")
                source_image_name = remove_ext(source_image)
                output_name = source_image_name + "_" + remove_ext(style_images_name[i]) + ".jpg"
                
                response = s3.put_object(
                    Body=output_bytes.getvalue(), 
                    Bucket=BUCKET_NAME, 
                    Key=username + "/" + source_image_name +"/" + output_name
                )

                result_images.append(username + "/" + output_name)

            return result_images
        

