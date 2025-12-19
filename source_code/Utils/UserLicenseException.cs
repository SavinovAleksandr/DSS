using System;

namespace DynStabSpace;

internal class UserLicenseException : Exception
{
	public UserLicenseException(string message)
		: base(message)
	{
	}
}
