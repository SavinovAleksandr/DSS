using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Markup;

namespace DynStabSpace;

public class MainWindow : Window, IComponentConnector
{
	internal ListBox Rgms;

	internal ListBox Events;

	private bool _contentLoaded;

	public MainWindow()
	{
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		InitializeComponent();
		try
		{
			if (License())
			{
				((FrameworkElement)this).DataContext = new DataInfo();
				return;
			}
			throw new UserLicenseException("Некорректный файл лицензии");
		}
		catch (Exception ex)
		{
			MessageBox.Show("Ошибка при выполнении операции!" + Environment.NewLine + Environment.NewLine + ex.Message, "Error", (MessageBoxButton)0, (MessageBoxImage)16);
			((Window)this).Close();
		}
	}

	private void DeselectRgms(object sender, MouseButtonEventArgs e)
	{
		((Selector)Rgms).SelectedItem = null;
	}

	private void DeselectEvents(object sender, MouseButtonEventArgs e)
	{
		((Selector)Events).SelectedItem = null;
	}

	private bool License()
	{
		bool flag = false;
		string machineName = Environment.MachineName;
		if (File.Exists("C:\\ПАРУС 6\\licence.txt"))
		{
			int length = machineName.Length;
			int num = Convert.ToInt32(length / 3);
			int num2 = length - 2 * num;
			string text = machineName.Substring(0, num);
			string text2 = machineName.Substring(num, num);
			if (text2.Substring(0, 1) == "-")
			{
				text += "-";
				text2 = text2.Replace("-", "");
			}
			string text3 = machineName.Substring(length - num2, num2);
			if (text3.Substring(0, 1) == "-")
			{
				text2 += "-";
				text3 = text3.Replace("-", "");
			}
			string[] array = File.ReadAllLines("C:\\ПАРУС 6\\licence.txt").ToArray();
			return array[43].Contains(text) && array[45].Contains(text2) && array[46].Contains(text3) && array[52].Contains("p5");
		}
		throw new UserLicenseException("Файл лицензии не обнаружен");
	}

	private void RemsClear(object sender, MouseButtonEventArgs e)
	{
		DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
		dataInfo.Rems.Name = null;
		dataInfo.VrnInf.Clear();
		dataInfo.VrnInf.Add(new VrnInfo
		{
			Id = -1,
			Name = "Нормальная схема",
			Num = 0,
			Deactive = false
		});
	}

	private void VirClear(object sender, MouseButtonEventArgs e)
	{
		DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
		dataInfo.VIR.Name = null;
	}

	private void SchClear(object sender, MouseButtonEventArgs e)
	{
		DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
		dataInfo.Sechen.Name = null;
		dataInfo.SchInf.Clear();
	}

	private void KprClear(object sender, MouseButtonEventArgs e)
	{
		DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
		dataInfo.GRF.Name = null;
		dataInfo.KprInf.Clear();
	}

	private void AutoClear(object sender, MouseButtonEventArgs e)
	{
		DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
		dataInfo.LAPNU.Name = null;
		dataInfo.DynWithPA = false;
		dataInfo.UseLPN = false;
		dataInfo.lpns = "";
	}

	[DebuggerNonUserCode]
	[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
	public void InitializeComponent()
	{
		if (!_contentLoaded)
		{
			_contentLoaded = true;
			Uri uri = new Uri("/DynStabSpace;component/mainwindow.xaml", UriKind.Relative);
			Application.LoadComponent((object)this, uri);
		}
	}

	[DebuggerNonUserCode]
	[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
	[EditorBrowsable(EditorBrowsableState.Never)]
	void IComponentConnector.Connect(int connectionId, object target)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Expected O, but got Unknown
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Expected O, but got Unknown
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Expected O, but got Unknown
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Expected O, but got Unknown
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Expected O, but got Unknown
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Expected O, but got Unknown
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Expected O, but got Unknown
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Expected O, but got Unknown
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Expected O, but got Unknown
		switch (connectionId)
		{
		case 1:
			Rgms = (ListBox)target;
			((Control)Rgms).MouseDoubleClick += new MouseButtonEventHandler(DeselectRgms);
			break;
		case 2:
			Events = (ListBox)target;
			((Control)Events).MouseDoubleClick += new MouseButtonEventHandler(DeselectEvents);
			break;
		case 3:
			((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(RemsClear);
			break;
		case 4:
			((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(AutoClear);
			break;
		case 5:
			((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(VirClear);
			break;
		case 6:
			((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(SchClear);
			break;
		case 7:
			((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(KprClear);
			break;
		default:
			_contentLoaded = true;
			break;
		}
	}
}
