from discord.ui import View, TextInput, Select, Button



class ExtView(View):
    def __init__(self, items = None, *, timeout = None):
        super().__init__(timeout=timeout)
        if isinstance(items, (list, tuple)):
            for item in items:
                if isinstance(item, (TextInput, Select, Button)):
                    self.add_item(item)
                else:
                    raise TypeError('<items> element must be following type: TextInput, Select, Button')
