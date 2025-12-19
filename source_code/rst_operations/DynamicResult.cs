namespace rst_operations;

public struct DynamicResult
{
	public string ResultMessage;

	public double TimeReached;

	public bool IsSuccess;

	public bool IsStable;

	public override string ToString()
	{
		return $"Результат: {ResultMessage}\r\nРассчитанное время: {TimeReached}\r\nУспешно: {IsSuccess} \r\nУстойчиво: {IsStable}";
	}
}
