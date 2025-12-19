using System;

namespace DynStabSpace;

internal class InitialDataException : Exception
{
	public InitialDataException(string message)
		: base(message)
	{
	}
}
