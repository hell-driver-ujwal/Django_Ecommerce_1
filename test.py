class King:
    def __init__(self, name, breed):
        self.name = name 
        self.breed = breed

    def bark(self):
        return f"{self.name} which is {self.breed} has bared ruff ruff "

myDog1 = King("Buddy1", "German")
myDog2= King("Buddy2", "German")
myDog3 = King("Buddy3", "German")
myDog4 = King("Buddy4", "German")
myDog5 = King("Buddy5", "German")

list = King.objects.filter(breed = "German")
print(list.len)