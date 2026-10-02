import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

const COLORS = ["#2563eb", "#3b82f6", "#60a5fa", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6"];

interface ChartRendererProps {
  chartType: string;
  data: any[];
  xAxis?: string;
  yAxis?: string;
  title?: string;
}

export const ChartRenderer: React.FC<ChartRendererProps> = ({
  chartType,
  data,
  xAxis = "",
  yAxis = "",
  title,
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400 text-sm italic">
        No records available to plot
      </div>
    );
  }

  const renderChart = () => {
    switch (chartType) {
      case "line":
        return (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey={xAxis} tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey={yAxis} stroke="#2563eb" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        );

      case "area":
        return (
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey={xAxis} tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey={yAxis} stroke="#2563eb" fill="#93c5fd" fillOpacity={0.4} />
            </AreaChart>
          </ResponsiveContainer>
        );

      case "horizontal_bar":
        return (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart layout="vertical" data={data} margin={{ top: 10, right: 30, left: 40, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis dataKey={xAxis} type="category" tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey={yAxis} fill="#2563eb" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case "pie":
      case "donut":
        const isDonut = chartType === "donut";
        return (
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Tooltip />
              <Legend />
              <Pie
                data={data}
                dataKey={yAxis || "count"}
                nameKey={xAxis || "name"}
                cx="50%"
                cy="50%"
                innerRadius={isDonut ? 60 : 0}
                outerRadius={100}
                paddingAngle={isDonut ? 3 : 0}
                label={({ name, percent }: any) => `${name} (${(percent * 100).toFixed(0)}%)`}
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        );

      case "scatter":
        return (
          <ResponsiveContainer width="100%" height={320}>
            <ScatterChart margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey={xAxis} name={xAxis} tick={{ fontSize: 12 }} />
              <YAxis dataKey={yAxis} name={yAxis} tick={{ fontSize: 12 }} />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} />
              <Legend />
              <Scatter name="Data Points" data={data} fill="#2563eb" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case "table":
        const keys = Object.keys(data[0] || {});
        return (
          <div className="overflow-x-auto max-h-80 border border-gray-200 rounded-xl">
            <table className="w-full text-left text-xs text-gray-700">
              <thead className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold sticky top-0">
                <tr>
                  {keys.map((k) => (
                    <th key={k} className="px-4 py-2.5 capitalize">{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.map((row, i) => (
                  <tr key={i} className="hover:bg-blue-50/50">
                    {keys.map((k) => (
                      <td key={k} className="px-4 py-2 truncate max-w-[200px]">
                        {row[k] !== null && row[k] !== undefined ? String(row[k]) : "-"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      case "bar":
      default:
        return (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey={xAxis} tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey={yAxis} fill="#2563eb" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <div className="w-full">
      {title && <h4 className="text-sm font-semibold text-gray-800 mb-3">{title}</h4>}
      {renderChart()}
    </div>
  );
};
