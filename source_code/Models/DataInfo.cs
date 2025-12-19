using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Windows;
using Microsoft.Win32;
using OfficeOpenXml.Style;
using Xls_prjt;
using rst_operations;

namespace DynStabSpace;

public class DataInfo : INotifyPropertyChanged
{
	private readonly string execution_root = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);

	private int _progress;

	private int _max;

	private string _label;

	public bool IsActive;

	public Settings SetWin;

	private RgmsInfo _selectedRGM;

	private ScnsInfo _selectedScn;

	private bool _UseTypeValU;

	private bool _UseSelNodes;

	private bool _DynNoPA;

	private bool _DynWithPA;

	private bool _SaveGRF;

	private RelayCommand _add;

	private RelayCommand _del;

	private RelayCommand _set;

	private RelayCommand _shunt_calc;

	private RelayCommand _time_kz_calc;

	private RelayCommand _dyn_calc;

	private RelayCommand _mdp_calc;

	private RelayCommand _u_ost_calc;

	public int Progress
	{
		get
		{
			return _progress;
		}
		set
		{
			_progress = value;
			OnPropertyChanged("Progress");
		}
	}

	public int Max
	{
		get
		{
			return _max;
		}
		set
		{
			_max = value;
			OnPropertyChanged("Max");
		}
	}

	public string Label
	{
		get
		{
			return _label;
		}
		set
		{
			_label = value;
			OnPropertyChanged("Label");
		}
	}

	public ObservableCollection<RgmsInfo> RgmsInfo { get; set; }

	public RgmsInfo SelectedRgm
	{
		get
		{
			return _selectedRGM;
		}
		set
		{
			_selectedRGM = value;
			OnPropertyChanged("SelectedRgm");
		}
	}

	public ObservableCollection<ScnsInfo> ScnsInfo { get; set; }

	public ScnsInfo SelectedScn
	{
		get
		{
			return _selectedScn;
		}
		set
		{
			_selectedScn = value;
			OnPropertyChanged("SelectedScn");
		}
	}

	public FileInfo Sechen { get; set; }

	public List<SchInfo> SchInf { get; set; }

	public FileInfo VIR { get; set; }

	public FileInfo GRF { get; set; }

	public List<KprInfo> KprInf { get; set; }

	public FileInfo LAPNU { get; set; }

	public FileInfo Rems { get; set; }

	public List<VrnInfo> VrnInf { get; set; }

	public bool UseTypeValU
	{
		get
		{
			return _UseTypeValU;
		}
		set
		{
			_UseTypeValU = value;
			OnPropertyChanged("UseTypeValU");
		}
	}

	public bool UseSelNodes
	{
		get
		{
			return _UseSelNodes;
		}
		set
		{
			_UseSelNodes = value;
			OnPropertyChanged("UseSelNodes");
		}
	}

	public bool CalcOnePhase { get; set; }

	public bool CalcTwoPhase { get; set; }

	public FileInfo ShuntKZ { get; set; }

	public List<ShuntKZ> ShuntKZInf { get; set; }

	public double BaseAngle { get; set; }

	public double CrtTimePrecision { get; set; }

	public double CrtTimeMax { get; set; }

	public int SelectedSch { get; set; }

	public bool DynNoPA
	{
		get
		{
			return _DynNoPA;
		}
		set
		{
			_DynNoPA = value;
			OnPropertyChanged("DynNoPA");
		}
	}

	public bool DynWithPA
	{
		get
		{
			return _DynWithPA;
		}
		set
		{
			_DynWithPA = value;
			OnPropertyChanged("DynWithPA");
		}
	}

	public bool SaveGRF
	{
		get
		{
			return _SaveGRF;
		}
		set
		{
			_SaveGRF = value;
			OnPropertyChanged("SaveGRF");
		}
	}

	public bool UseLPN { get; set; }

	public string tmp_root { get; set; }

	public string lpns { get; set; }

	public List<ShuntResults> ShuntResults { get; set; }

	public List<CrtTimeResults> CrtTimeResults { get; set; }

	public List<DynResults> DynResults { get; set; }

	public List<MdpResults> MdpResults { get; set; }

	public List<UostResults> UostResults { get; set; }

	public RelayCommand Add => _add ?? (_add = new RelayCommand(delegate
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Expected O, but got Unknown
		//IL_0c88: Unknown result type (might be due to invalid IL or missing references)
		OpenFileDialog val = new OpenFileDialog();
		((FileDialog)val).Title = "Выбор файлов";
		((FileDialog)val).Filter = "Rastr|*.rg2;*.rst;*.sch;*.ut2;*.scn;*.vrn;*.kpr;*.csv;*.lpn;*.dwf";
		val.Multiselect = true;
		try
		{
			if (((CommonDialog)val).ShowDialog() == true)
			{
				string[] fileNames = ((FileDialog)val).FileNames;
				foreach (string file in fileNames)
				{
					if ((Path.GetExtension(file) == ".rg2" || Path.GetExtension(file) == ".rst") && !RgmsInfo.Any((RgmsInfo k) => k.Name == file))
					{
						RgmsInfo.Add(new RgmsInfo
						{
							Name = file
						});
					}
					else if (Path.GetExtension(file) == ".scn" && !ScnsInfo.Any((ScnsInfo k) => k.Name == file))
					{
						ScnsInfo.Add(new ScnsInfo
						{
							Name = file
						});
					}
					else if (Path.GetExtension(file) == ".ut2")
					{
						VIR.Name = file;
					}
					else if (Path.GetExtension(file) == ".sch")
					{
						Sechen.Name = file;
						SchInf.Clear();
						RastrOperations rastrOperations = new RastrOperations();
						rastrOperations.Load(file);
						foreach (int item in rastrOperations.Selection("sechen"))
						{
							SchInf.Add(new SchInfo
							{
								Id = item,
								Name = rastrOperations.getVal("sechen", "name", item),
								Num = rastrOperations.getVal("sechen", "ns", item),
								Control = rastrOperations.getVal("sechen", "sta", item)
							});
						}
					}
					else if (Path.GetExtension(file) == ".vrn")
					{
						Rems.Name = file;
						VrnInf.Clear();
						VrnInf.Add(new VrnInfo
						{
							Id = -1,
							Name = "Нормальная схема",
							Num = 0,
							Deactive = false
						});
						RastrOperations rastrOperations2 = new RastrOperations();
						rastrOperations2.Load(file);
						foreach (int item2 in rastrOperations2.Selection("var_mer"))
						{
							VrnInf.Add(new VrnInfo
							{
								Id = item2,
								Name = rastrOperations2.getVal("var_mer", "name", item2),
								Num = rastrOperations2.getVal("var_mer", "Num", item2),
								Deactive = rastrOperations2.getVal("var_mer", "sta", item2)
							});
						}
					}
					else if (Path.GetExtension(file) == ".kpr")
					{
						GRF.Name = file;
						KprInf.Clear();
						RastrOperations rastrOperations3 = new RastrOperations();
						rastrOperations3.Load(file);
						foreach (int item3 in rastrOperations3.Selection("ots_val"))
						{
							KprInf.Add(new KprInfo
							{
								Id = item3,
								Num = rastrOperations3.getVal("ots_val", "Num", item3),
								Name = rastrOperations3.getVal("ots_val", "name", item3),
								Table = rastrOperations3.getVal("ots_val", "tabl", item3),
								Selection = rastrOperations3.getVal("ots_val", "vibork", item3),
								Col = rastrOperations3.getVal("ots_val", "formula", item3)
							});
						}
					}
					else if (Path.GetExtension(file) == ".csv")
					{
						string[] array = File.ReadAllLines(file);
						string[] array2 = array[0].Split(new char[1] { ';' });
						if (array2.Length != 7 || !(array2[0] == "node") || !(array2[1] == "r1") || !(array2[2] == "x1") || !(array2[3] == "u1") || !(array2[4] == "r2") || !(array2[5] == "x2") || !(array2[6] == "u2"))
						{
							throw new UncorrectFileException("Некорректный файл для задания шунтов КЗ");
						}
						string numberDecimalSeparator = CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator;
						string oldValue = ((numberDecimalSeparator == ".") ? "," : ".");
						ShuntKZ.Name = file;
						UseSelNodes = false;
						for (int num = 1; num < array.Count(); num++)
						{
							string[] array3 = array[num].Split(new char[1] { ';' });
							ShuntKZInf.Add(new ShuntKZ
							{
								Node = Convert.ToInt32(array3[0]),
								r1 = ((array3[1] != "" && array3[1] != "0") ? Convert.ToDouble(array3[1].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
								x1 = ((array3[2] != "" && array3[2] != "0") ? Convert.ToDouble(array3[2].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
								u1 = ((array3[3] != "" && array3[3] != "0") ? Convert.ToDouble(array3[3].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
								r2 = ((array3[4] != "" && array3[4] != "0") ? Convert.ToDouble(array3[4].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
								x2 = ((array3[5] != "" && array3[5] != "0") ? Convert.ToDouble(array3[5].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
								u2 = ((array3[6] != "" && array3[6] != "0") ? Convert.ToDouble(array3[6].Replace(oldValue, numberDecimalSeparator)) : (-1.0))
							});
						}
					}
					else if (Path.GetExtension(file) == ".dwf" || Path.GetExtension(file) == ".lpn")
					{
						DynWithPA = true;
						LAPNU.Name = file;
						UseLPN = Path.GetExtension(file) == ".lpn";
						if (UseLPN)
						{
							RastrOperations rastrOperations4 = new RastrOperations();
							rastrOperations4.Load(file);
							List<int> list = new List<int>();
							foreach (int item4 in rastrOperations4.Selection("LAPNU", "sta = 0"))
							{
								list.Add(rastrOperations4.getVal("LAPNU", "Id", item4));
							}
							lpns = "=" + string.Join(";", list);
						}
					}
				}
			}
		}
		catch (Exception ex)
		{
			MessageBox.Show("Ошибка при выполнении операции!" + Environment.NewLine + Environment.NewLine + ex.Message, "Error", (MessageBoxButton)0, (MessageBoxImage)16);
		}
	}));

	public RelayCommand Del => _del ?? (_del = new RelayCommand(delegate
	{
		RgmsInfo.Remove(_selectedRGM);
		ScnsInfo.Remove(_selectedScn);
	}));

	public RelayCommand Settings => _set ?? (_set = new RelayCommand(delegate
	{
		SetWin = new Settings();
		((FrameworkElement)SetWin).DataContext = this;
		((Window)SetWin).Show();
	}));

	public RelayCommand ShuntCalc => _shunt_calc ?? (_shunt_calc = new RelayCommand(delegate
	{
		if (!IsActive)
		{
			BackgroundWorker backgroundWorker = new BackgroundWorker
			{
				WorkerReportsProgress = true
			};
			backgroundWorker.DoWork += Shunt_KZ;
			backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
			{
				Progress = e.ProgressPercentage;
				Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
			};
			backgroundWorker.RunWorkerCompleted += EventFinish;
			backgroundWorker.RunWorkerAsync();
		}
	}));

	public RelayCommand TimeKzCalc => _time_kz_calc ?? (_time_kz_calc = new RelayCommand(delegate
	{
		if (!IsActive)
		{
			BackgroundWorker backgroundWorker = new BackgroundWorker
			{
				WorkerReportsProgress = true
			};
			backgroundWorker.DoWork += Max_KZ_Time;
			backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
			{
				Progress = e.ProgressPercentage;
				Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
			};
			backgroundWorker.RunWorkerCompleted += EventFinish;
			backgroundWorker.RunWorkerAsync();
		}
	}));

	public RelayCommand DynamicCalc => _dyn_calc ?? (_dyn_calc = new RelayCommand(delegate
	{
		if (!IsActive)
		{
			BackgroundWorker backgroundWorker = new BackgroundWorker
			{
				WorkerReportsProgress = true
			};
			backgroundWorker.DoWork += DynStabilityCalc;
			backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
			{
				Progress = e.ProgressPercentage;
				Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
			};
			backgroundWorker.RunWorkerCompleted += EventFinish;
			backgroundWorker.RunWorkerAsync();
		}
	}));

	public RelayCommand MdpCalc => _mdp_calc ?? (_mdp_calc = new RelayCommand(delegate
	{
		if (!IsActive)
		{
			BackgroundWorker backgroundWorker = new BackgroundWorker
			{
				WorkerReportsProgress = true
			};
			backgroundWorker.DoWork += MdpStabilityCalc;
			backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
			{
				Progress = e.ProgressPercentage;
				Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
			};
			backgroundWorker.RunWorkerCompleted += EventFinish;
			backgroundWorker.RunWorkerAsync();
		}
	}));

	public RelayCommand UostCalc => _u_ost_calc ?? (_u_ost_calc = new RelayCommand(delegate
	{
		if (!IsActive)
		{
			BackgroundWorker backgroundWorker = new BackgroundWorker
			{
				WorkerReportsProgress = true
			};
			backgroundWorker.DoWork += UostStabilityCalc;
			backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
			{
				Progress = e.ProgressPercentage;
				Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
			};
			backgroundWorker.RunWorkerCompleted += EventFinish;
			backgroundWorker.RunWorkerAsync();
		}
	}));

	public event PropertyChangedEventHandler PropertyChanged;

	public DataInfo()
	{
		bool flag = File.Exists(execution_root + "\\EPPlus.dll");
		bool flag2 = File.Exists(execution_root + "\\EPPlus.Interfaces.dll");
		bool flag3 = File.Exists(execution_root + "\\OxyPlot.dll");
		bool flag4 = File.Exists(execution_root + "\\OxyPlot.Wpf.dll");
		if (!(flag && flag2 && flag3 && flag4))
		{
			throw new FileNotFoundException("Не обнаружены необходимые для работы DSS библиотеки." + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + "EPPlus.dll - " + (flag ? "Обнаружена" : "Отсутствует") + Environment.NewLine + "EPPlus.Interfaces.dll - " + (flag2 ? "Обнаружена" : "Отсутствует") + Environment.NewLine + "OxyPlot.dll - " + (flag3 ? "Обнаружена" : "Отсутствует") + Environment.NewLine + "OxyPlot.Wpf.dll - " + (flag4 ? "Обнаружена" : "Отсутствует"));
		}
		IsActive = false;
		RgmsInfo = new ObservableCollection<RgmsInfo>();
		ScnsInfo = new ObservableCollection<ScnsInfo>();
		VIR = new FileInfo();
		Sechen = new FileInfo();
		GRF = new FileInfo();
		Rems = new FileInfo();
		SchInf = new List<SchInfo>();
		VrnInf = new List<VrnInfo>
		{
			new VrnInfo
			{
				Id = -1,
				Name = "Нормальная схема",
				Num = 0,
				Deactive = false
			}
		};
		KprInf = new List<KprInfo>();
		LAPNU = new FileInfo();
		UseTypeValU = true;
		UseSelNodes = true;
		CalcOnePhase = true;
		CalcTwoPhase = true;
		ShuntKZ = new FileInfo();
		ShuntKZInf = new List<ShuntKZ>();
		CrtTimePrecision = 0.02;
		CrtTimeMax = 1.0;
		DynNoPA = true;
		DynWithPA = false;
		SaveGRF = false;
		UseLPN = false;
		tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + "\\DynStabSpace";
		Directory.CreateDirectory(tmp_root);
		lpns = "";
		SelectedSch = 0;
		ShuntResults = new List<ShuntResults>();
		CrtTimeResults = new List<CrtTimeResults>();
		DynResults = new List<DynResults>();
		MdpResults = new List<MdpResults>();
		UostResults = new List<UostResults>();
		Progress = 0;
		Max = 1;
		Label = "";
	}

	private void UostStabilityCalc(object sender, DoWorkEventArgs e)
	{
		IsActive = true;
		ClearAllResults();
		UostStabilityCalc uostStabilityCalc = new UostStabilityCalc(sender, RgmsInfo, ScnsInfo, VrnInf, Rems, KprInf);
		Max = uostStabilityCalc.Max;
		Progress = 0;
		UostResults = uostStabilityCalc.Calc();
		ResultToFiles(uostStabilityCalc.root);
		e.Result = uostStabilityCalc.root;
		(sender as BackgroundWorker).ReportProgress(Progress + 1);
	}

	private void MdpStabilityCalc(object sender, DoWorkEventArgs e)
	{
		IsActive = true;
		ClearAllResults();
		MdpStabilityCalc mdpStabilityCalc = new MdpStabilityCalc(sender, RgmsInfo, ScnsInfo, VrnInf, Rems, VIR, Sechen, LAPNU, SchInf, KprInf, lpns, SelectedSch, DynNoPA, DynWithPA, UseLPN);
		Max = mdpStabilityCalc.Max;
		Progress = 0;
		MdpResults = mdpStabilityCalc.Calc();
		ResultToFiles(mdpStabilityCalc.root);
		e.Result = mdpStabilityCalc.root;
		(sender as BackgroundWorker).ReportProgress(Progress + 1);
	}

	private void DynStabilityCalc(object sender, DoWorkEventArgs e)
	{
		IsActive = true;
		ClearAllResults();
		DynStabilityCalc dynStabilityCalc = new DynStabilityCalc(sender, RgmsInfo, ScnsInfo, VrnInf, Rems, KprInf, Sechen, LAPNU, SaveGRF, lpns, DynNoPA, DynWithPA, UseLPN);
		Max = dynStabilityCalc.Max;
		Progress = 0;
		DynResults = dynStabilityCalc.Calc();
		ResultToFiles(dynStabilityCalc.root);
		e.Result = dynStabilityCalc.root;
		(sender as BackgroundWorker).ReportProgress(Progress + 1);
	}

	private void Max_KZ_Time(object sender, DoWorkEventArgs e)
	{
		IsActive = true;
		ClearAllResults();
		Max_KZ_Time max_KZ_Time = new Max_KZ_Time(sender, RgmsInfo, ScnsInfo, VrnInf, Rems, CrtTimePrecision, CrtTimeMax);
		Max = max_KZ_Time.Max;
		Progress = 0;
		CrtTimeResults = max_KZ_Time.Calc();
		ResultToFiles(max_KZ_Time.root);
		e.Result = max_KZ_Time.root;
		(sender as BackgroundWorker).ReportProgress(Progress + 1);
	}

	private void Shunt_KZ(object sender, DoWorkEventArgs e)
	{
		IsActive = true;
		ClearAllResults();
		Shunt_KZ shunt_KZ = new Shunt_KZ(sender, RgmsInfo, VrnInf, Rems, ShuntKZInf, UseSelNodes, UseTypeValU, CalcOnePhase, CalcTwoPhase);
		Max = shunt_KZ.Max;
		Progress = 0;
		ShuntResults = shunt_KZ.Calc();
		ResultToFiles(shunt_KZ.root);
		e.Result = shunt_KZ.root;
		(sender as BackgroundWorker).ReportProgress(Progress + 1);
	}

	private void EventFinish(object sender, RunWorkerCompletedEventArgs e)
	{
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		if (e.Error == null)
		{
			MessageBox.Show("Операция выполнена успешно!" + Environment.NewLine + Environment.NewLine + $"Результаты доступны в каталоге {e.Result}", "DSS", (MessageBoxButton)0, (MessageBoxImage)64);
		}
		else
		{
			MessageBox.Show("Ошибка при выполнении операции!" + Environment.NewLine + Environment.NewLine + e.Error.Message, "DSS Algorithm Error", (MessageBoxButton)0, (MessageBoxImage)16);
		}
		Label = "";
		Progress = 0;
		IsActive = false;
	}

	private void ResultToFiles(string root)
	{
		int num = ((ShuntResults.Count() > 0) ? 1 : 0) + ((CrtTimeResults.Count() > 0) ? 2 : 0) + ((DynResults.Count() > 0) ? 3 : 0) + ((MdpResults.Count() > 0) ? 4 : 0) + ((UostResults.Count() > 0) ? 5 : 0);
		int num2 = 2;
		ExcelOperations excelOperations = new ExcelOperations("Результаты расчетов");
		excelOperations.Font();
		excelOperations.setVal(1, 1, "Наименование режима");
		excelOperations.Width(1, 40);
		excelOperations.setVal(1, 2, "Схема сети");
		excelOperations.Width(2, 40);
		switch (num)
		{
		case 1:
			excelOperations.Merge(1, 1, 2, 1, hor: true, vert: true);
			excelOperations.Merge(1, 2, 2, 2, hor: true, vert: true);
			excelOperations.setVal(1, 3, "Номер узла");
			excelOperations.Merge(1, 3, 2, 3, hor: true, vert: true);
			excelOperations.Width(3, 15);
			excelOperations.setVal(1, 4, "Однофазное КЗ");
			excelOperations.Merge(1, 4, 1, 6, hor: true, vert: true);
			excelOperations.setVal(2, 4, "R, Ом");
			excelOperations.Width(4, 15);
			excelOperations.setVal(2, 5, "X, Ом");
			excelOperations.Width(5, 15);
			excelOperations.setVal(2, 6, "U1, кВ");
			excelOperations.Width(6, 15);
			excelOperations.setVal(1, 7, "Двухфазное КЗ");
			excelOperations.Merge(1, 7, 1, 9, hor: true, vert: true);
			excelOperations.setVal(2, 7, "R, Ом");
			excelOperations.Width(7, 15);
			excelOperations.setVal(2, 8, "X, Ом");
			excelOperations.Width(8, 15);
			excelOperations.setVal(2, 9, "U1, кВ");
			excelOperations.Width(9, 15);
			excelOperations.Format(1, 1, 2, 9, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
			excelOperations.Borders(1, 1, 2, 9);
			num2++;
			foreach (ShuntResults shuntResult in ShuntResults)
			{
				excelOperations.setVal(num2, 1, shuntResult.RgName);
				int bRow7 = num2;
				foreach (Shems shem in shuntResult.Shems)
				{
					int bRow8 = num2;
					excelOperations.setVal(num2, 2, shem.ShemeName);
					if (shem.IsStable)
					{
						foreach (ShuntKZ node in shem.Nodes)
						{
							excelOperations.setVal(num2, 3, node.Node);
							excelOperations.setVal(num2, 4, $"{node.r1:F3}");
							excelOperations.setVal(num2, 5, $"{node.x1:F3}");
							excelOperations.setVal(num2, 6, $"{node.u1:F1}");
							excelOperations.setVal(num2, 7, $"{node.r2:F3}");
							excelOperations.setVal(num2, 8, $"{node.x2:F3}");
							excelOperations.setVal(num2, 9, $"{node.u2:F1}");
							excelOperations.Format(num2, 3, num2, 9, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
							num2++;
						}
					}
					else
					{
						excelOperations.setVal(num2, 3, "Схема не балансируется");
						excelOperations.Merge(num2, 3, num2, 9, hor: true, vert: true);
						num2++;
					}
					excelOperations.Merge(bRow8, 2, num2 - 1, 2, hor: true, vert: true);
				}
				excelOperations.Merge(bRow7, 1, num2 - 1, 1, hor: true, vert: true);
				excelOperations.Borders(bRow7, 1, num2 - 1, 9);
			}
			if (!CalcOnePhase)
			{
				excelOperations.HideColumn(4);
				excelOperations.HideColumn(5);
				excelOperations.HideColumn(6);
			}
			if (!CalcTwoPhase)
			{
				excelOperations.HideColumn(7);
				excelOperations.HideColumn(8);
				excelOperations.HideColumn(9);
			}
			break;
		case 2:
			excelOperations.setVal(1, 3, "Расчетное КЗ");
			excelOperations.Width(3, 40);
			excelOperations.setVal(1, 4, "Предельное время отключения, с");
			excelOperations.Width(4, 15);
			excelOperations.Format(1, 1, 1, 4, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
			excelOperations.Borders(1, 1, 1, 4);
			foreach (CrtTimeResults crtTimeResult in CrtTimeResults)
			{
				excelOperations.setVal(num2, 1, crtTimeResult.RgName);
				int bRow3 = num2;
				foreach (CrtShems crtShem in crtTimeResult.CrtShems)
				{
					int bRow4 = num2;
					excelOperations.setVal(num2, 2, crtShem.ShemeName);
					if (crtShem.IsStable)
					{
						foreach (CrtTimes time in crtShem.Times)
						{
							excelOperations.setVal(num2, 3, time.ScnName);
							excelOperations.setVal(num2, 4, (CrtTimeMax != time.CrtTime) ? $"{time.CrtTime:F3}" : $">{time.CrtTime}");
							num2++;
						}
					}
					else
					{
						excelOperations.setVal(num2, 3, "Схема не балансируется");
						excelOperations.Merge(num2, 3, num2, 4, hor: true, vert: true);
						num2++;
					}
					excelOperations.Merge(bRow4, 2, num2 - 1, 2, hor: true, vert: true);
				}
				excelOperations.Merge(bRow3, 1, num2 - 1, 1, hor: true, vert: true);
				excelOperations.Format(bRow3, 1, num2 - 1, 4, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
				excelOperations.Borders(bRow3, 1, num2 - 1, 4);
			}
			break;
		case 3:
			excelOperations.Merge(1, 1, 2, 1, hor: true, vert: true);
			excelOperations.Merge(1, 2, 2, 2, hor: true, vert: true);
			excelOperations.setVal(1, 3, "Расчетный сценарий");
			excelOperations.Merge(1, 3, 2, 3, hor: true, vert: true);
			excelOperations.Width(3, 15);
			excelOperations.setVal(1, 4, "Без учета действия ПА");
			excelOperations.Merge(1, 4, 1, 6, hor: true, vert: true);
			excelOperations.setVal(2, 4, "Результат расчета ДУ");
			excelOperations.Width(4, 20);
			excelOperations.setVal(2, 5, "Критерий нарушения ДУ");
			excelOperations.Width(5, 40);
			excelOperations.setVal(2, 6, "Рисунок");
			excelOperations.Width(6, 20);
			excelOperations.setVal(1, 7, "С учетом действия ПА");
			excelOperations.Merge(1, 7, 1, 9, hor: true, vert: true);
			excelOperations.setVal(2, 7, "Результат расчета ДУ");
			excelOperations.Width(7, 20);
			excelOperations.setVal(2, 8, "Критерий нарушения ДУ");
			excelOperations.Width(8, 40);
			excelOperations.setVal(2, 9, "Рисунок");
			excelOperations.Width(9, 20);
			excelOperations.Format(1, 1, 2, 9, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
			excelOperations.Borders(1, 1, 2, 9);
			num2++;
			foreach (DynResults dynResult in DynResults)
			{
				excelOperations.setVal(num2, 1, dynResult.RgName);
				int bRow5 = num2;
				foreach (DynShems dynShem in dynResult.DynShems)
				{
					int bRow6 = num2;
					excelOperations.setVal(num2, 2, dynShem.ShemeName);
					if (dynShem.IsStable)
					{
						foreach (Events @event in dynShem.Events)
						{
							excelOperations.setVal(num2, 3, @event.Name);
							if (@event.NoPaResult.IsSuccess)
							{
								excelOperations.setVal(num2, 4, @event.NoPaResult.IsStable ? "Устойчиво" : "Неустойчиво");
								excelOperations.setVal(num2, 5, @event.NoPaResult.IsStable ? "-" : @event.NoPaResult.ResultMessage);
								string text = "";
								foreach (string item in @event.NoPaPic)
								{
									text += ((@event.NoPaPic.IndexOf(item) > 0) ? (Environment.NewLine ?? "") : "");
									text += Path.GetFileNameWithoutExtension(item);
								}
								excelOperations.setVal(num2, 6, text);
							}
							if (@event.WithPaResult.IsSuccess)
							{
								excelOperations.setVal(num2, 7, @event.WithPaResult.IsStable ? "Устойчиво" : "Неустойчиво");
								excelOperations.setVal(num2, 8, @event.WithPaResult.IsStable ? "-" : @event.WithPaResult.ResultMessage);
								string text2 = "";
								foreach (string item2 in @event.WithPaPic)
								{
									text2 += ((@event.WithPaPic.IndexOf(item2) > 0) ? (Environment.NewLine ?? "") : "");
									text2 += Path.GetFileNameWithoutExtension(item2);
								}
								excelOperations.setVal(num2, 9, text2);
							}
							excelOperations.Format(num2, 3, num2, 9, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
							num2++;
						}
					}
					else
					{
						excelOperations.setVal(num2, 3, "Схема не балансируется");
						excelOperations.Merge(num2, 3, num2, 9, hor: true, vert: true);
						num2++;
					}
					excelOperations.Merge(bRow6, 2, num2 - 1, 2, hor: true, vert: true);
				}
				excelOperations.Merge(bRow5, 1, num2 - 1, 1, hor: true, vert: true);
				excelOperations.Borders(bRow5, 1, num2 - 1, 9);
			}
			if (!SaveGRF)
			{
				excelOperations.HideColumn(6);
				excelOperations.HideColumn(9);
			}
			if (!DynNoPA)
			{
				excelOperations.HideColumn(4);
				excelOperations.HideColumn(5);
				excelOperations.HideColumn(6);
			}
			if (!DynWithPA)
			{
				excelOperations.HideColumn(7);
				excelOperations.HideColumn(8);
				excelOperations.HideColumn(9);
			}
			break;
		case 4:
		{
			int num6 = SchInf.Where((SchInfo k) => k.Control).Count();
			int num3 = KprInf.Count();
			excelOperations.Merge(1, 1, 3, 1, hor: true, vert: true);
			excelOperations.Merge(1, 2, 3, 2, hor: true, vert: true);
			excelOperations.setVal(1, 3, "Расчетный сценарий");
			excelOperations.Merge(1, 3, 3, 3, hor: true, vert: true);
			excelOperations.Width(3, 15);
			excelOperations.setVal(1, 4, "Без учета действия ПА");
			excelOperations.setVal(2, 4, "МДП, МВт");
			excelOperations.Width(4, 15);
			excelOperations.Merge(2, 4, 3, 4, hor: true, vert: true);
			excelOperations.setVal(1, 5 + num6 + num3, "С учетом действия ПА");
			excelOperations.setVal(2, 5 + num6 + num3, "МДП, МВт");
			excelOperations.Width(5 + num6 + num3, 15);
			excelOperations.Merge(2, 5 + num6 + num3, 3, 5 + num6 + num3, hor: true, vert: true);
			if (num6 > 0)
			{
				int num7 = 0;
				excelOperations.setVal(2, 5, "Перетоки в КС, МВт");
				excelOperations.setVal(2, 6 + num6 + num3, "Перетоки в КС, МВт");
				foreach (SchInfo item3 in SchInf.Where((SchInfo k) => k.Control))
				{
					excelOperations.setVal(3, 5 + num7, item3.Name);
					excelOperations.setVal(3, 6 + num6 + num3 + num7, item3.Name);
					excelOperations.Width(5 + num7, 15);
					excelOperations.Width(6 + num6 + num3 + num7, 15);
					num7++;
				}
				excelOperations.Merge(2, 5, 2, 5 + num7 - 1, hor: true, vert: true);
				excelOperations.Merge(2, 6 + num6 + num3, 2, 6 + num6 + num3 + num7 - 1, hor: true, vert: true);
			}
			if (num3 > 0)
			{
				int num8 = 0;
				excelOperations.setVal(2, 5 + num6, "Контролируемые величины");
				excelOperations.setVal(2, 6 + 2 * num6 + num3, "Контролируемые величины");
				foreach (KprInfo item4 in KprInf)
				{
					excelOperations.setVal(3, 5 + num6 + num8, item4.Name);
					excelOperations.setVal(3, 6 + 2 * num6 + num3 + num8, item4.Name);
					excelOperations.Width(5 + num6 + num8, 15);
					excelOperations.Width(6 + 2 * num6 + num3, 15);
					num8++;
				}
				excelOperations.Merge(2, 5 + num6, 2, 5 + num6 + num8 - 1, hor: true, vert: true);
				excelOperations.Merge(2, 6 + 2 * num6 + num3, 2, 6 + 2 * num6 + num3 + num8 - 1, hor: true, vert: true);
			}
			if (num6 > 0 || num3 > 0)
			{
				excelOperations.Merge(1, 4, 1, 4 + num6 + num3, hor: true, vert: true);
				excelOperations.Merge(1, 5 + num6 + num3, 1, 5 + 2 * num6 + 2 * num3);
			}
			excelOperations.Format(1, 1, 3, 5 + 2 * num6 + 2 * num3, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
			excelOperations.Borders(1, 1, 3, 5 + 2 * num6 + 2 * num3);
			num2 += 2;
			foreach (MdpResults mdpResult in MdpResults)
			{
				excelOperations.setVal(num2, 1, mdpResult.RgName);
				int bRow9 = num2;
				foreach (MdpShems mdpShem in mdpResult.MdpShems)
				{
					int bRow10 = num2;
					excelOperations.setVal(num2, 2, mdpShem.ShemeName);
					if (mdpShem.IsStable)
					{
						foreach (MdpEvents event2 in mdpShem.Events)
						{
							excelOperations.setVal(num2, 3, event2.Name);
							excelOperations.setVal(num2, 4, $"{event2.NoPaMdp:F0}");
							excelOperations.setVal(num2, 5 + num6 + num3, $"{event2.WithPaMdp:F0}");
							if (num6 > 0)
							{
								for (int num9 = 0; num9 < num6; num9++)
								{
									excelOperations.setVal(num2, 5 + num9, (event2.NoPaSechen.Count() != 0) ? $"{event2.NoPaSechen.ElementAt(num9).Value:F0}" : "");
									excelOperations.setVal(num2, 6 + num6 + num3 + num9, (event2.WithPaSechen.Count() != 0) ? $"{event2.WithPaSechen.ElementAt(num9).Value:F0}" : "");
								}
							}
							if (num3 > 0)
							{
								for (int num10 = 0; num10 < num3; num10++)
								{
									excelOperations.setVal(num2, 5 + num6 + num10, (event2.NoPaKpr.Count() != 0) ? $"{event2.NoPaKpr.ElementAt(num10).Value:F2}" : "");
									excelOperations.setVal(num2, 6 + 2 * num6 + num3 + num10, (event2.WithPaKpr.Count() != 0) ? $"{event2.WithPaKpr.ElementAt(num10).Value:F2}" : "");
								}
							}
							excelOperations.Format(num2, 3, num2, 5 + 2 * num6 + 2 * num3, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
							num2++;
						}
					}
					else
					{
						excelOperations.setVal(num2, 3, "Схема не балансируется");
						excelOperations.Merge(num2, 3, num2, 5 + 2 * num6 + 2 * num3, hor: true, vert: true);
						num2++;
					}
					excelOperations.Merge(bRow10, 2, num2 - 1, 2, hor: true, vert: true);
				}
				excelOperations.Merge(bRow9, 1, num2 - 1, 1, hor: true, vert: true);
				excelOperations.Borders(bRow9, 1, num2 - 1, 5 + 2 * num6 + 2 * num3);
			}
			if (!DynNoPA)
			{
				for (int num11 = 4; num11 <= 4 + num6 + num3; num11++)
				{
					excelOperations.HideColumn(num11);
				}
			}
			if (!DynWithPA)
			{
				for (int num12 = 5 + num6 + num3; num12 <= 5 + 2 * num6 + 2 * num3; num12++)
				{
					excelOperations.HideColumn(num12);
				}
			}
			break;
		}
		case 5:
		{
			int num3 = KprInf.Count();
			excelOperations.Merge(1, 1, 2, 1, hor: true, vert: true);
			excelOperations.Merge(1, 2, 2, 2, hor: true, vert: true);
			excelOperations.setVal(1, 3, "Расчетный сценарий");
			excelOperations.Width(3, 15);
			excelOperations.Merge(1, 3, 2, 3, hor: true, vert: true);
			excelOperations.setVal(1, 4, "ЛЭП");
			excelOperations.setVal(2, 4, "Узел начала");
			excelOperations.Width(4, 15);
			excelOperations.setVal(2, 5, "Узел конца");
			excelOperations.Width(5, 15);
			excelOperations.setVal(2, 6, "Np");
			excelOperations.Width(6, 7);
			excelOperations.Merge(1, 4, 1, 6, hor: true, vert: true);
			excelOperations.setVal(1, 7, "Область устойчивости, %");
			excelOperations.Width(7, 15);
			excelOperations.Merge(1, 7, 2, 7, hor: true, vert: true);
			excelOperations.setVal(1, 8, "Остаточное напряжение в узлах ЛЭП, кВ");
			excelOperations.setVal(2, 8, "Узел начала");
			excelOperations.Width(8, 15);
			excelOperations.setVal(2, 9, "Узел конца");
			excelOperations.Width(9, 15);
			excelOperations.Merge(1, 8, 1, 9, hor: true, vert: true);
			if (num3 > 0)
			{
				int num4 = 0;
				excelOperations.setVal(1, 10, "Контролируемые величины");
				foreach (KprInfo item5 in KprInf)
				{
					excelOperations.setVal(2, 10 + num4, item5.Name);
					num4++;
				}
				excelOperations.Merge(1, 10, 1, 10 + num4 - 1, hor: true, vert: true);
			}
			excelOperations.Format(1, 1, 2, 9 + num3, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
			excelOperations.Borders(1, 1, 2, 9 + num3);
			num2++;
			foreach (UostResults uostResult in UostResults)
			{
				excelOperations.setVal(num2, 1, uostResult.RgName);
				int bRow = num2;
				foreach (UostShems uostShem in uostResult.UostShems)
				{
					int bRow2 = num2;
					excelOperations.setVal(num2, 2, uostShem.ShemeName);
					if (uostShem.IsStable)
					{
						foreach (UostEvents event3 in uostShem.Events)
						{
							excelOperations.setVal(num2, 3, event3.Name);
							excelOperations.setVal(num2, 4, event3.BeginNode);
							excelOperations.setVal(num2, 5, event3.EndNode);
							excelOperations.setVal(num2, 6, event3.Np);
							if (event3.Distance == -1.0)
							{
								excelOperations.setVal(num2, 7, ">100");
							}
							else if (event3.Distance == 100.0)
							{
								excelOperations.setVal(num2, 7, "<0");
							}
							else
							{
								excelOperations.setVal(num2, 7, $"{event3.Distance * 100.0:F2}");
							}
							excelOperations.setVal(num2, 8, $"{event3.BeginUost:F2}");
							excelOperations.setVal(num2, 9, $"{event3.EndUost:F2}");
							if (num3 > 0)
							{
								int num5 = 0;
								foreach (Values value in event3.Values)
								{
									excelOperations.setVal(num2, 10 + num5, value.Value);
									num5++;
								}
							}
							excelOperations.Format(num2, 3, num2, 9 + num3, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
							num2++;
						}
					}
					else
					{
						excelOperations.setVal(num2, 3, "Схема не балансируется");
						excelOperations.Merge(num2, 3, num2, 9 + num3, hor: true, vert: true);
						num2++;
					}
					excelOperations.Merge(bRow2, 2, num2 - 1, 2, hor: true, vert: true);
				}
				excelOperations.Merge(bRow, 1, num2 - 1, 1, hor: true, vert: true);
				excelOperations.Borders(bRow, 1, num2 - 1, 9 + num3);
			}
			break;
		}
		}
		excelOperations.Save(root + "\\Результат расчетов.xlsx");
		string[] files = Directory.GetFiles(root, "*.rst");
		foreach (string path in files)
		{
			File.Delete(path);
		}
		string[] files2 = Directory.GetFiles(root, "*.scn");
		foreach (string path2 in files2)
		{
			File.Delete(path2);
		}
	}

	private void ClearAllResults()
	{
		UostResults.Clear();
		MdpResults.Clear();
		CrtTimeResults.Clear();
		ShuntResults.Clear();
		DynResults.Clear();
	}

	public void OnPropertyChanged([CallerMemberName] string prop = "")
	{
		if (this.PropertyChanged != null)
		{
			this.PropertyChanged(this, new PropertyChangedEventArgs(prop));
		}
	}
}
