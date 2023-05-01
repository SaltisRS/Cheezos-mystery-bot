from .DataStructure import Generation
from dataclasses import asdict
import json


class GenerationEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Generation):
            return asdict(obj)
        return super().default(obj)