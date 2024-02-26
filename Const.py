class _const:
    class ConstError(TypeError):
        pass

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise self.ConstError("Const change (%s)" % key)
        self.__dict__[key] = value


Const = _const()

Const.kGameCol = 10
Const.kGameRow = 16
Const.kGameSum = 10
Const.kGameImageName = 'game.jpg'
