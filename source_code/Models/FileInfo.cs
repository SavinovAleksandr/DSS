using System.ComponentModel;
using System.IO;
using System.Runtime.CompilerServices;

namespace DynStabSpace;

public class FileInfo : INotifyPropertyChanged
{
	private string _name;

	public string Name
	{
		get
		{
			return _name;
		}
		set
		{
			_name = value;
			OnPropertyChanged("Name");
			OnPropertyChanged("name");
		}
	}

	public string name => Path.GetFileName(_name);

	public event PropertyChangedEventHandler PropertyChanged;

	public void OnPropertyChanged([CallerMemberName] string prop = "")
	{
		if (this.PropertyChanged != null)
		{
			this.PropertyChanged(this, new PropertyChangedEventArgs(prop));
		}
	}
}
