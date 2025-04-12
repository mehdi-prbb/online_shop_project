from django.contrib.auth.models import UserManager



class CustomUserManager(UserManager):
	"""
	Custom manager for CustomUser model.
    Provides helper methods for creating regular users and superusers.
	"""
	def create_user(self, phone, password):
		"""
		Creates and returns a regular user with the given email and password.
		"""
		if not phone:
			raise ValueError('user must have phone number')
		user = self.model(
				phone=phone
				)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, phone, password):
		"""
		Creates and returns a superuser with the given email and password.
		"""
		user = self.create_user(phone, password)
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)