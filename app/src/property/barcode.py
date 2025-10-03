# Описание основных свойств ШК:
# 1) Номер штрихкода состоит из 12 символов;
# 2) Используется только латинский алфавит;
# 3) В составе номера штрихкода запрещены буквы: O, Q, L, J, U, V.


class BarcodeProperty:
    def __init__(self, string: str):
        self.length = 12
        self.forbidden_characters = ["O", "Q", "L", "J", "U", "V"]
        self.string = self._valid_characters(string)

    def _valid_characters(self, s: str) -> str:
        condition = (
            s.isalnum()
            and len(s) == self.length
            and all(
                (c.isdigit() or c.isupper()) and c not in self.forbidden_characters
                for c in s
            )
        )
        if condition:
            return s
        raise ValueError(
            f"Строка '{s}' содержит недопустимые символы. Допустимы только цифры, а также большие латинские буквы, кроме букв: {', '.join(self.forbidden_characters)}."
        )
