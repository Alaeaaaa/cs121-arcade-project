class LinkedList:
    __head: int
    __tail: LinkedList 

    def __init__(self, head: int, tail: LinkedList) -> None:
        self.__head = head
        self.__tail = tail

    def is_empty(self):
        if self.head is None or self.tail is None:
            return True
        return False 
    
    @property
    def head(self)->int:
        return self.__head
    @property
    def tail(self)->LinkedList:
        return self.__tail

    def prepend(self, new: int):
        L:LinkedList
        L.head=new
        L.tail=self
    
    def __len__(self):
        l=1
        for i in self.tail:
            l+=1
        return l
    def __getitem__(self, i: int):
        L:LinkedList
        if i==1:
            return self.head
        else:
            l=1
            while l =! i:
                for k in self.tail:
                    l+=1
                    L.prepend(k)
            return L.head 
    
            
