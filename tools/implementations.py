from .interface import BaseTool


class IdeaGenerationTool(BaseTool):
    name = 'Idea Generation'
    description = 'Capture an individual reflection as the start of an idea-generation session.'
    version = '1.0'

    def validate(self):
        text = (self.user_input.get('initial_thought') or '').strip()
        if len(text) < 5:
            self.errors['initial_thought'] = 'Please write a slightly longer reflection.'

    def process(self):
        text = (self.user_input.get('initial_thought') or '').strip()
        return {
            'initial_thought': text,
            'word_count': len(text.split()),
            'character_count': len(text),
        }


class FiveStructuralElementsTool(BaseTool):
    name = 'Five Structural Elements'
    description = 'Pairs share challenges and hopes to build new connections.'
    version = '1.0'

    FIELDS = (
        'pair_one_challenge',
        'pair_one_hope',
        'pair_two_challenge',
        'pair_two_hope',
    )

    def validate(self):
        for field in self.FIELDS:
            value = (self.user_input.get(field) or '').strip()
            if len(value) < 3:
                self.errors[field] = 'Please write a slightly longer response.'

    def process(self):
        result = {}
        total_words = 0
        for field in self.FIELDS:
            value = (self.user_input.get(field) or '').strip()
            words = len(value.split())
            result[field] = value
            result[f'{field}_word_count'] = words
            total_words += words
        result['word_count'] = total_words
        return result


