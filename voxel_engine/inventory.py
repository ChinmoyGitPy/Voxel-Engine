from .blocks import placeable_blocks,block_names

class Inventory:
    def __init__(self,blocks=None):
        self.slots = list(blocks) if blocks is not None else list(placeable_blocks)
        self.selected_index = 0

    @property
    def selected_block(self):
        return self.slots[self.selected_index]
    
    @property
    def selected_name(self):
        return block_names.get(self.selected_block,"?")
    
    def select_index(self,index):
        if 0 <= index < len(self.slots):
            self.selected_index = index
    
    def scroll(self,direction):
        n = len(self.slots)
        self.selected_index = (self.selected_index + direction) % n

    def __len__(self):
        return len(self.slots)
    
    def __iter__(self):
        return iter(self.slots)
    
    