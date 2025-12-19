using System;

namespace DynStabSpace;

internal class UncorrectFileException : Exception
{
	public UncorrectFileException(string message)
		: base(message)
	{
	}
}
