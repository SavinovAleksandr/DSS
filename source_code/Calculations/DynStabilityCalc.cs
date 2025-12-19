using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Threading;
using OxyPlot;
using OxyPlot.Axes;
using OxyPlot.Legends;
using OxyPlot.Series;
using OxyPlot.Wpf;
using rst_operations;

namespace DynStabSpace;

public class DynStabilityCalc
{
	private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} Пакетный расчет ДУ";

	private BackgroundWorker _w;

	private ObservableCollection<RgmsInfo> RgmsInfo;

	private ObservableCollection<ScnsInfo> ScnsInfo;

	private List<VrnInfo> VrnInf;

	private FileInfo Rems;

	private FileInfo Sechen;

	private FileInfo LAPNU;

	private List<KprInfo> _KprInf;

	private bool SaveGRF;

	private string lpns;

	private bool DynNoPA;

	private bool DynWithPA;

	public bool UseLPN;

	private List<KprInfo> KprInf
	{
		get
		{
			return _KprInf;
		}
		set
		{
			grf = new List<int>();
			foreach (KprInfo item in value)
			{
				if (!grf.Contains(item.Num))
				{
					grf.Add(item.Num);
				}
			}
			grf.OrderBy((int k) => k);
			_KprInf = value;
		}
	}

	private List<int> grf { get; set; }

	public string root => tmp_root;

	public int Max
	{
		get
		{
			int num = (DynNoPA ? 1 : 0) + (DynWithPA ? 1 : 0);
			return RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ScnsInfo.Count() * num + 1;
		}
	}

	public DynStabilityCalc(object sender, ObservableCollection<RgmsInfo> rgms, ObservableCollection<ScnsInfo> scns, List<VrnInfo> vrns, FileInfo rems, List<KprInfo> kprs, FileInfo sechen, FileInfo lapnu, bool save = false, string lpns = "", bool no_pa = true, bool with_pa = false, bool lpn = false)
	{
		if (rgms.Count() == 0 || scns.Count() == 0 || (lpn && sechen.Name == null) || (save && kprs.Count() == 0) || (with_pa && lapnu.Name == null))
		{
			throw new InitialDataException("Не заданы все исходные данные для выполнения пакетного расчета динамической устойчивости!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}{Environment.NewLine}" + $"Загружено аварийных процесслов - {scns.Count()}" + ((lpn && sechen.Name == null) ? (Environment.NewLine + "Используется файл ПА в формате lpn, но не загружен файл сечений!") : "") + ((lapnu.Name == null && with_pa) ? (Environment.NewLine + "Включен расчет МДП с учетом ПА, но файл ПА отсутствует!") : "") + ((save && kprs.Count() == 0) ? (Environment.NewLine + "Включена опция сохранения графиков, но отсутствует файл графического вывода!") : ""));
		}
		RgmsInfo = rgms;
		ScnsInfo = scns;
		VrnInf = vrns;
		Rems = rems;
		Sechen = sechen;
		LAPNU = lapnu;
		KprInf = kprs;
		SaveGRF = save;
		this.lpns = lpns;
		DynNoPA = no_pa;
		DynWithPA = with_pa;
		UseLPN = lpn;
		_w = sender as BackgroundWorker;
		Directory.CreateDirectory(tmp_root);
	}

	public List<DynResults> Calc()
	{
		int num = 0;
		List<DynResults> list = new List<DynResults>();
		foreach (RgmsInfo item in RgmsInfo)
		{
			List<DynShems> list2 = new List<DynShems>();
			int num2 = RgmsInfo.IndexOf(item) + 1;
			foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
			{
				DynShems dynShems = new DynShems();
				List<Events> list3 = new List<Events>();
				dynShems.ShemeName = item2.Name;
				foreach (ScnsInfo item3 in ScnsInfo)
				{
					int num3 = ScnsInfo.IndexOf(item3) + 1;
					RastrOperations rastrOperations = new RastrOperations();
					rastrOperations.Load(item.Name);
					rastrOperations.DynSettings();
					dynShems.IsStable = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
					if (!dynShems.IsStable)
					{
						break;
					}
					DynamicResult noPaResult = default(DynamicResult);
					DynamicResult withPaResult = default(DynamicResult);
					List<string> list4 = new List<string>();
					List<string> list5 = new List<string>();
					if (DynNoPA)
					{
						rastrOperations.Load(item3.Name);
						rastrOperations.LoadTemplate(".dfw");
						if (SaveGRF)
						{
							noPaResult = rastrOperations.RunDynamic();
							foreach (int _id in grf)
							{
								string text = tmp_root + $"\\Рисунок - {num2}.{item2.Num + 1}.{num3}.{_id}(без ПА).png";
								GetPictures(rastrOperations, KprInf.Where((KprInfo k) => k.Num == _id).ToList(), text);
								list4.Add(text);
							}
						}
						else
						{
							noPaResult = rastrOperations.RunDynamic(_ems: true);
						}
						num++;
						_w.ReportProgress(num);
					}
					if (DynWithPA)
					{
						if (UseLPN)
						{
							rastrOperations.Load(Sechen.Name);
							rastrOperations.CreateScnFromLpn(LAPNU.Name, lpns, item3.Name);
						}
						else
						{
							rastrOperations.Load(item3.Name);
							rastrOperations.Load(LAPNU.Name);
						}
						if (SaveGRF)
						{
							withPaResult = rastrOperations.RunDynamic();
							foreach (int _id2 in grf)
							{
								string text2 = tmp_root + $"\\Рисунок - {num2}.{item2.Num + 1}.{num3}.{_id2}(с ПА).png";
								GetPictures(rastrOperations, KprInf.Where((KprInfo k) => k.Num == _id2).ToList(), text2);
								list5.Add(text2);
							}
						}
						else
						{
							withPaResult = rastrOperations.RunDynamic(_ems: true);
						}
						num++;
						_w.ReportProgress(num);
					}
					list3.Add(new Events
					{
						Name = item3.name,
						NoPaResult = noPaResult,
						WithPaResult = withPaResult,
						NoPaPic = list4,
						WithPaPic = list5
					});
				}
				dynShems.Events = list3;
				list2.Add(dynShems);
			}
			list.Add(new DynResults
			{
				RgName = item.name,
				DynShems = list2
			});
		}
		return list;
	}

	private void GetPictures(RastrOperations _rst, List<KprInfo> _pictures, string _file)
	{
		PlotModel grf = new PlotModel();
		grf.Legends.Add(new Legend
		{
			LegendPosition = LegendPosition.RightBottom,
			LegendPlacement = LegendPlacement.Inside,
			LegendBackground = OxyColors.White,
			LegendBorder = OxyColors.Black
		});
		grf.Axes.Add(new LinearAxis
		{
			Position = AxisPosition.Bottom,
			MajorGridlineStyle = LineStyle.Solid,
			AbsoluteMinimum = 0.0,
			Title = "Время, с",
			AxisTitleDistance = 10.0,
			TitleFontSize = 18.0
		});
		grf.Axes.Add(new LinearAxis
		{
			Position = AxisPosition.Left,
			MajorGridlineStyle = LineStyle.Solid
		});
		PngExporter exp = new PngExporter
		{
			Width = 1200,
			Height = 800
		};
		foreach (KprInfo _picture in _pictures)
		{
			LineSeries lineSeries = new LineSeries
			{
				StrokeThickness = 2.0,
				Title = _picture.Name,
				FontSize = 16.0
			};
			foreach (rst_operations.Point item in _rst.GetPointsFromExitFile(_picture.Table, _picture.Col, _picture.Selection))
			{
				lineSeries.Points.Add(new DataPoint(item.X, item.Y));
			}
			grf.Series.Add(lineSeries);
		}
		((DispatcherObject)Application.Current).Dispatcher.Invoke((Action)delegate
		{
			MemoryStream memoryStream = new MemoryStream();
			exp.Export(grf, memoryStream);
			Image.FromStream((Stream)memoryStream).Save(_file, ImageFormat.Png);
		});
	}
}
