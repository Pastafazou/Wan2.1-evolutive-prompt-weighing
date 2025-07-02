import json

class StringHolder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "hold"
    CATEGORY = "utility"

    def hold(self, value):
        return (value,)


class MetadataLogger:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9223372036854775807
                }),
                "ranking": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 5
                }),
                "video_path": ("STRING", {"default": "feedback/clip.webp"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("json_record",)
    OUTPUT_NODE = True
    FUNCTION = "make_json"
    CATEGORY = "logging"

    def make_json(self, prompt, seed, ranking, video_path):
        json_record = {
            "prompt": prompt,
            "seed": seed,
            "ranking": ranking,
            "video_path": video_path
        }
        return (json.dumps(json_record, ensure_ascii=False),)


NODE_CLASS_MAPPINGS = {
    "StringHolder": StringHolder,
    "MetadataLogger": MetadataLogger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StringHolder": "String Holder",
    "MetadataLogger": "Metadata Logger",
}
