class AnonymousUser:
    is_authenticated = False
    def is_admin(self):
        return False
    def is_teacher(self):
        return False
    def is_staff(self):
        return False
