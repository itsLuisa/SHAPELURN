
class BackAndForth_Iterator:
    def __init__(self,somelist):
        self.index = -1
        self.list = somelist

    def next(self):
        if self.list == []:
            raise StopIteration
        self.index += 1
        if self.index >= len(self.list):
            self.index = 0
        return self.list[self.index]

    def previous(self):
        if self.list == []:
            raise StopIteration
        self.index -= 1
        if self.index < 0:
            self.index = len(self.somelist)-1
        return self.list[self.index]
    
        
