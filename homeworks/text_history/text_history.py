from abc import ABC, abstractmethod

class TextHistory:
    def __init__(self):
        self._text = ''
        self._version = 0
        self._history = []
    
    @property
    def text(self):
        return self._text
    
    @property
    def version(self):
        return self._version
        
    def insert(self, text, pos = None):
        if pos is None:
            pos = len(self._text)
        if pos < 0 or pos > len(self._text):
            raise ValueError('unbelievable position!')
        
        self._version += 1
        act = InsertAction(text, pos, self._version - 1, self._version)
        self._text = act.apply(self._text)
        self._history.append(act)
        
        return self._version
    
    def replace(self, text, pos = None):
        if pos is None:
            pos = len(self._text)
        if pos < 0 or pos > len(self._text):
            raise ValueError('unbelievable position!')

        self._version += 1
        act = ReplaceAction(text, pos, self._version - 1, self._version)
        self._text = act.apply(self._text)
        self._history.append(act)
        
        return self._version

    def delete(self, pos, length):
        if pos is None or pos < 0 or pos > len(self._text):
            raise ValueError('unbelievable position!')
        if length < 0 or pos + length > len(self._text):
            raise ValueError('unbelievable length!')
            
        self._version += 1
        act = DeleteAction(pos, length, self._version - 1, self._version)
        self._text = act.apply(self._text)
        self._history.append(act)
        
        return self._version
    
    def action(self, action):
        if action.from_version != self._version or action.to_version <= self._version:
            raise ValueError('unbelievable versions!')
        
        self._text = action.apply(self._text)
        self._version = action.to_version
        
        return self._version
        
    def get_actions(self, from_version = None, to_version = None):
        if from_version is None:
            from_version = 0
        if to_version is None:
            to_version = self._version
        if from_version < 0 or to_version > self._version or from_version > to_version:
            raise ValueError('unbelievable versions!')
        
        return [act for act in self._history if act.from_version >= from_version and act.to_version <= to_version]
            
        
        
        
class Action(ABC):
    def __init__(self, from_version, to_version):
        if from_version > to_version or from_version < 0:
            raise ValueError('unbelievable versions!')
            
        self.from_version = from_version
        self.to_version = to_version
    
    @abstractmethod
    def apply(self):
        pass

class InsertAction(Action):
    def __init__(self, text, pos, from_version, to_version):
        super().__init__(from_version, to_version)
        self.text = text
        self.pos = pos
    
    
    def apply(self, str):
        str_new = str[:self.pos] + self.text + str[self.pos:]
        return str_new

class ReplaceAction(Action):
    def __init__(self, text, pos, from_version, to_version):
        super().__init__(from_version, to_version)
        self.text = text
        self.pos = pos
    
    
    def apply(self, str):
        str_new = str[:self.pos] + self.text + str[self.pos + len(self.text):]
        return str_new
        
class DeleteAction(Action):
    def __init__(self, pos, len, from_version, to_version):
        super().__init__(from_version, to_version)
        self.pos = pos
        self.len = len
        
        
    def apply(self, str):
        str_new = str[:self.pos] + str[self.pos + self.len:]
        return str_new

if __name__ == '__main__':
    h = TextHistory()
    print(h.insert('abc'))
    print(h.text)
    print(h.insert('def', 1))
    print(h.text)
    print(h.replace('hui', 4))
    print(h.text)
    print(h._history)
    print(h.get_actions(1, 3))