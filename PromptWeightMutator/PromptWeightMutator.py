import json, math, regex as re, pathlib

class PromptWeightMutator:
    """
    Rewrites a prompt string by applying learned token weights.
    Input: base_prompt + token_weights.json
    Output: weighted prompt string for use in generation
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True}),
                "weight_file": ("STRING", {
                    "default": "feedback/token_weights.json",
                    "multiline": False
                }),
                "boost_scale": ("FLOAT", {
                    "default": 0.4, "min": 0.0, "max": 1.5
                }),
                "damp_scale": ("FLOAT", {
                    "default": 0.4, "min": 0.0, "max": 1.5
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "mutate"
    CATEGORY = "preference"

    word_re = re.compile(r"\p{L}[\p{L}\p{Mn}\p{Pd}'’]*", re.UNICODE)

    def _load_weights(self, path):
        p = pathlib.Path(path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _apply_weight(self, token, w, boost, damp):
        if w > 0:
            scale = 1 + boost * math.tanh(w)
        else:
            scale = 1 - damp * math.tanh(-w)
        scale = round(scale, 2)
        return f"({token}:{scale})" if abs(scale - 1.0) > 0.05 else token

    def mutate(self, base_prompt, weight_file, boost_scale, damp_scale):
        weights = self._load_weights(weight_file)
        if not weights:
            return (base_prompt,)

        def repl(match):
            word = match.group(0)
            key = word.lower()
            if key not in weights:
                return word
            return self._apply_weight(word, weights[key], boost_scale, damp_scale)

        new_prompt = self.word_re.sub(repl, base_prompt)
        return (new_prompt,)

# Register the node in ComfyUI
NODE_CLASS_MAPPINGS = {
    "PromptWeightMutator": PromptWeightMutator,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptWeightMutator": "Prompt Weight Mutator",
}
