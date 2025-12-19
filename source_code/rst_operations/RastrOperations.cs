using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using ASTRALib;

namespace rst_operations;

internal class RastrOperations
{
	private Rastr _rastr;

	public RastrOperations()
	{
		_rastr = (Rastr)Activator.CreateInstance(Marshal.GetTypeFromCLSID(new Guid("EFC5E4AD-A3DD-11D3-B73F-00500454CF3F")));
	}

	~RastrOperations()
	{
		_rastr = null;
	}

	public static string FindTemplatePathWithExtension(string extension)
	{
		if (!Directory.Exists(Environment.GetFolderPath(Environment.SpecialFolder.Personal) + "\\RastrWIN3\\SHABLON\\"))
		{
			return null;
		}
		string[] files = Directory.GetFiles(Environment.GetFolderPath(Environment.SpecialFolder.Personal) + "\\RastrWIN3\\SHABLON\\");
		return files.FirstOrDefault((string filename) => Path.GetExtension(filename) == extension && Path.GetFileNameWithoutExtension(filename) != "базовый режим мт");
	}

	public void Load(string file)
	{
		string shabl = FindTemplatePathWithExtension(Path.GetExtension(file));
		_rastr.NewFile(shabl);
		_rastr.Load(RG_KOD.RG_REPL, file, FindTemplatePathWithExtension(Path.GetExtension(file)));
	}

	public void LoadTemplate(string _extension)
	{
		_rastr.NewFile(FindTemplatePathWithExtension(_extension));
	}

	public void Save(string file)
	{
		_rastr.Save(file, FindTemplatePathWithExtension(Path.GetExtension(file)));
	}

	public void Add(string file)
	{
		_rastr.Load(RG_KOD.RG_ADD, file, FindTemplatePathWithExtension(Path.GetExtension(file)));
	}

	public bool rgm(string _param = "", dynamic _iterations = null, dynamic _voltage = null)
	{
		table table = (dynamic)_rastr.Tables.Item("com_regim");
		col col = (dynamic)table.Cols.Item("it_max");
		col col2 = (dynamic)table.Cols.Item("dv_min");
		if (_iterations != null)
		{
			((ICol)col).set_Z(0, (object)_iterations);
		}
		if (_voltage != null)
		{
			((ICol)col2).set_Z(0, (object)_voltage);
		}
		return _rastr.rgm(_param) == RastrRetCode.AST_OK;
	}

	public int AddTableRow(string table)
	{
		table table2 = (dynamic)_rastr.Tables.Item(table);
		table2.AddRow();
		return table2.Size - 1;
	}

	public void SetLineForUostCalc(int id1, int id2, double r, double x, double L)
	{
		table table = (dynamic)_rastr.Tables.Item("vetv");
		col col = (dynamic)table.Cols.Item("r");
		col col2 = (dynamic)table.Cols.Item("x");
		double num = L * r / 100.0;
		double num2 = L * x / 100.0;
		((ICol)col).set_Z(id1, (object)num);
		((ICol)col).set_Z(id2, (object)(r - num));
		((ICol)col2).set_Z(id1, (object)num2);
		((ICol)col2).set_Z(id2, (object)(x - num2));
		_rastr.rgm("");
	}

	public void ChangeRXForUostCalc(int x_id, double x, int r_id = 0, double r = -1.0)
	{
		table table = (dynamic)_rastr.Tables.Item("DFWAutoActionScn");
		col col = (dynamic)table.Cols.Item("Formula");
		((ICol)col).set_Z(x_id, (object)x.ToString().Replace(",", "."));
		if (r != -1.0)
		{
			((ICol)col).set_Z(r_id, (object)r.ToString().Replace(",", "."));
		}
	}

	public List<int> Selection(string table, string selection = "")
	{
		table table2 = (dynamic)_rastr.Tables.Item(table ?? "");
		table2.SetSel(selection ?? "");
		int num = ((ITable)table2).get_FindNextSel(-1);
		List<int> list = new List<int>();
		while (num != -1)
		{
			list.Add(num);
			num = ((ITable)table2).get_FindNextSel(num);
		}
		return list;
	}

	public bool ApplyVariant(int num, string file)
	{
		Load(file);
		_rastr.ApplyVariant(num);
		return rgm();
	}

	public dynamic getVal(string table, string col, string selection)
	{
		table table2 = (dynamic)_rastr.Tables.Item(table);
		col col2 = (dynamic)table2.Cols.Item(col);
		table2.SetSel(selection ?? "");
		int num = ((ITable)table2).get_FindNextSel(-1);
		return (num != -1) ? ((ICol)col2).get_Z(num) : null;
	}

	public dynamic getVal(string table, string col, int index)
	{
		table table2 = (dynamic)_rastr.Tables.Item(table);
		col col2 = (dynamic)table2.Cols.Item(col);
		return ((ICol)col2).get_Z(index);
	}

	public void setVal(string table, string col, int index, dynamic val)
	{
		table table2 = (dynamic)_rastr.Tables.Item(table);
		col col2 = (dynamic)table2.Cols.Item(col);
		((ICol)col2).set_Z(index, (object)val);
	}

	public bool setVal(string table, string col, string selection, dynamic val)
	{
		table table2 = (dynamic)_rastr.Tables.Item(table ?? "");
		col col2 = (dynamic)table2.Cols.Item(col ?? "");
		table2.SetSel(selection ?? "");
		int num = ((ITable)table2).get_FindNextSel(-1);
		if (num != -1)
		{
			((ICol)col2).set_Z(num, (object)val);
		}
		return num != -1;
	}

	public void setValВyCalc(string table, string col, string selection, dynamic val)
	{
		table table2 = (dynamic)_rastr.Tables.Item(table);
		col col2 = (dynamic)table2.Cols.Item(col);
		table2.SetSel(selection);
		col2.Calc(val);
	}

	public void CreateScnFromLpn(string lpn_file, string lpn, string scn_file, string file = "")
	{
		LoadTemplate(".vrn");
		Load(lpn_file);
		table table = (dynamic)_rastr.Tables.Item("var_mer");
		col col = (dynamic)table.Cols.Item("Num");
		col col2 = (dynamic)table.Cols.Item("Type");
		table.AddRow();
		((ICol)col).set_Z(0, (object)1);
		((ICol)col2).set_Z(0, (object)1);
		_rastr.LAPNUSMZU("1" + lpn);
		Add(scn_file);
		if (file != "")
		{
			Save(file);
		}
	}

	public double Run_Ut()
	{
		table table = (dynamic)_rastr.Tables.Item("vetv");
		table table2 = (dynamic)_rastr.Tables.Item("ut_common");
		col col = (dynamic)table2.Cols.Item("sum_kfc");
		for (RastrRetCode rastrRetCode = _rastr.step_ut("i"); rastrRetCode == RastrRetCode.AST_OK; rastrRetCode = _rastr.step_ut("z"))
		{
		}
		return (dynamic)((ICol)col).get_Z(0);
	}

	public double Step(double _step = 1.0, bool init = true)
	{
		RastrRetCode rastrRetCode = RastrRetCode.AST_OK;
		table table = (dynamic)_rastr.Tables.Item("ut_common");
		col col = (dynamic)table.Cols.Item("sum_kfc");
		if (init)
		{
			rastrRetCode = _rastr.step_ut("i");
		}
		setVal("ut_common", "kfc", 0, _step);
		rastrRetCode = _rastr.step_ut("z");
		return (dynamic)((ICol)col).get_Z(0);
	}

	public void DynSettings()
	{
		table table = (dynamic)_rastr.Tables.Item("com_dynamics");
		col col = (dynamic)table.Cols.Item("MaxResultFiles");
		col col2 = (dynamic)table.Cols.Item("SnapAutoLoad");
		col col3 = (dynamic)table.Cols.Item("SnapMaxCount");
		((ICol)col).set_Z(0, (object)1);
		((ICol)col2).set_Z(0, (object)1);
		((ICol)col3).set_Z(0, (object)1);
	}

	public DynamicResult RunDynamic(bool _ems = false, double _MaxTime = -1.0)
	{
		DynamicResult result = default(DynamicResult);
		table table = (dynamic)_rastr.Tables.Item("com_dynamics");
		col col = (dynamic)table.Cols.Item("Tras");
		double num = (dynamic)((ICol)col).get_Z(0);
		LoadTemplate(".dfw");
		if (_ems && _MaxTime != -1.0)
		{
			((ICol)col).set_Z(0, (object)_MaxTime);
		}
		FWDynamic fWDynamic = _rastr.FWDynamic();
		RastrRetCode rastrRetCode = (_ems ? fWDynamic.RunEMSmode() : fWDynamic.Run());
		result.IsSuccess = rastrRetCode == RastrRetCode.AST_OK;
		result.IsStable = fWDynamic.SyncLossCause == DFWSyncLossCause.SYNC_LOSS_NONE;
		result.ResultMessage = ((fWDynamic.ResultMessage == "") ? " - " : fWDynamic.ResultMessage);
		result.TimeReached = fWDynamic.TimeReached;
		((ICol)col).set_Z(0, (object)num);
		return result;
	}

	public double FindCrtTime(double precision, double max_time)
	{
		double num = max_time;
		LoadTemplate(".dfw");
		ResetCrtTime(max_time);
		FWDynamic fWDynamic = _rastr.FWDynamic();
		RastrRetCode rastrRetCode = fWDynamic.RunEMSmode();
		if (fWDynamic.SyncLossCause != DFWSyncLossCause.SYNC_LOSS_NONE)
		{
			double num2 = max_time;
			double num3 = 0.0;
			double num4 = (num2 - num3) * 0.5;
			while (Math.Abs(num4) > precision || fWDynamic.SyncLossCause != DFWSyncLossCause.SYNC_LOSS_NONE)
			{
				num += num4 * (double)((fWDynamic.SyncLossCause == DFWSyncLossCause.SYNC_LOSS_NONE) ? 1 : (-1));
				ResetCrtTime(num);
				fWDynamic = _rastr.FWDynamic();
				rastrRetCode = fWDynamic.RunEMSmode();
				if (fWDynamic.SyncLossCause == DFWSyncLossCause.SYNC_LOSS_NONE)
				{
					num3 = num;
				}
				else
				{
					num2 = num;
				}
				num4 = (num2 - num3) * 0.5;
			}
		}
		return num;
	}

	private void ResetCrtTime(double dt)
	{
		double num = 1.0;
		List<int> list = Selection("DFWAutoActionScn");
		foreach (int item in list)
		{
			string text = getVal("DFWAutoActionScn", "ObjectClass", item);
			if (text == "node")
			{
				setVal("DFWAutoActionScn", "TimeStart", item, num);
				setVal("DFWAutoActionScn", "DT", item, dt);
			}
			else if (text == "vetv")
			{
				setVal("DFWAutoActionScn", "TimeStart", item, num + dt);
				setVal("DFWAutoActionScn", "DT", item, 999);
			}
		}
		setVal("com_dynamics", "Tras", 0, num + dt + 3.0);
	}

	public ShuntKZResult FindShuntKZ(int node, double u_ost, double x_isx, double r_isx = -1.0)
	{
		table table = (dynamic)_rastr.Tables.Item("com_dynamics");
		col col = (dynamic)table.Cols.Item("Tras");
		((ICol)col).set_Z(0, (object)1.1);
		LoadTemplate(".dfw");
		List<string> _prot = new List<string>();
		new ComAwareEventInfo(typeof(_IRastrEvents_Event), "OnLog").AddEventHandler(_rastr, (_IRastrEvents_OnLogEventHandler)delegate(LogErrorCodes Code, int Level, int StageId, string TableName, int TableIndex, string Description, string FormName)
		{
			if (Code == LogErrorCodes.LOG_INFO && Description.Contains("Величина остаточного напряжения в узле"))
			{
				_prot.Add(Description);
			}
		});
		double num = Math.Sqrt(((r_isx != -1.0) ? Math.Pow(r_isx, 2.0) : 0.0) + Math.Pow(x_isx, 2.0));
		double num2 = ((r_isx == -1.0) ? (Math.PI / 2.0) : Math.Atan(x_isx / r_isx));
		if (r_isx == -1.0)
		{
			CreateShuntScn(node, num * Math.Sin(num2));
		}
		else
		{
			CreateShuntScn(node, num * Math.Sin(num2), num * Math.Cos(num2));
		}
		FWDynamic fWDynamic = _rastr.FWDynamic();
		RastrRetCode rastrRetCode = fWDynamic.Run();
		double num3 = Convert.ToDouble(_prot.LastOrDefault().Split(new char[1] { '(' })[1].Split(new char[1] { ',' })[0].Replace(" кВ", "").Replace("Uкз=", "").Replace(".", CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator ?? ""));
		double num4 = getVal("node", "uhom", $"ny={node}");
		while (Math.Abs(num3 - u_ost) > Math.Min(2.0, 0.02 * num4))
		{
			num = num * u_ost / num3;
			if (r_isx == -1.0)
			{
				CreateShuntScn(node, num * Math.Sin(num2));
			}
			else
			{
				CreateShuntScn(node, num * Math.Sin(num2), num * Math.Cos(num2));
			}
			rastrRetCode = fWDynamic.Run();
			num3 = Convert.ToDouble(_prot.LastOrDefault().Split(new char[1] { '(' })[1].Split(new char[1] { ',' })[0].Replace(" кВ", "").Replace("Uкз=", "").Replace(".", CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator ?? ""));
			_prot.Clear();
		}
		return new ShuntKZResult
		{
			r = ((r_isx == -1.0) ? (-1.0) : (num * Math.Cos(num2))),
			x = num * Math.Sin(num2),
			u = num3
		};
	}

	private void CreateShuntScn(int node, double x, double r = -1.0)
	{
		LoadTemplate(".scn");
		table table = (dynamic)_rastr.Tables.Item("DFWAutoActionScn");
		col col = (dynamic)table.Cols.Item("Id");
		col col2 = (dynamic)table.Cols.Item("Type");
		col col3 = (dynamic)table.Cols.Item("Formula");
		col col4 = (dynamic)table.Cols.Item("ObjectClass");
		col col5 = (dynamic)table.Cols.Item("ObjectProp");
		col col6 = (dynamic)table.Cols.Item("ObjectKey");
		col col7 = (dynamic)table.Cols.Item("RunsCount");
		col col8 = (dynamic)table.Cols.Item("TimeStart");
		col col9 = (dynamic)table.Cols.Item("DT");
		table.AddRow();
		((ICol)col).set_Z(0, (object)table.Size);
		((ICol)col2).set_Z(0, (object)1);
		((ICol)col3).set_Z(0, (object)x.ToString().Replace(",", "."));
		((ICol)col4).set_Z(0, (object)"node");
		((ICol)col5).set_Z(0, (object)"x");
		((ICol)col6).set_Z(0, (object)node);
		((ICol)col7).set_Z(0, (object)1);
		((ICol)col8).set_Z(0, (object)1);
		((ICol)col9).set_Z(0, (object)0.06);
		if (r != -1.0)
		{
			table.AddRow();
			((ICol)col).set_Z(1, (object)table.Size);
			((ICol)col2).set_Z(1, (object)1);
			((ICol)col3).set_Z(1, (object)r.ToString().Replace(",", "."));
			((ICol)col4).set_Z(1, (object)"node");
			((ICol)col5).set_Z(1, (object)"r");
			((ICol)col6).set_Z(1, (object)node);
			((ICol)col7).set_Z(1, (object)1);
			((ICol)col8).set_Z(1, (object)1);
			((ICol)col9).set_Z(1, (object)0.06);
		}
	}

	public List<Point> GetPointsFromExitFile(string table, string col, string selection)
	{
		table table2 = (dynamic)_rastr.Tables.Item(table);
		table2.SetSel(selection);
		List<Point> list = new List<Point>();
		int num = ((ITable)table2).get_FindNextSel(-1);
		if (num < 0)
		{
			return list;
		}
		double[,] array = (dynamic)_rastr.GetChainedGraphSnapshot(table, col, num, 0);
		for (int i = 0; i < array.GetLength(0); i++)
		{
			list.Add(new Point(array[i, 1], array[i, 0]));
		}
		return list;
	}
}
