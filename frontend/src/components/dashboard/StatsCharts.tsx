/**
 * Stats Charts Component
 * Visual charts for dashboard statistics using Recharts
 */

import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Stats } from '../../types/api.types';
import { motion } from 'framer-motion';

interface StatsChartsProps {
  stats: Stats;
}

export const StatsCharts = ({ stats }: StatsChartsProps) => {
  // Prepare NSFW distribution data for pie chart
  const nsfwData = Object.entries(stats.nsfw_distribution || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }));

  // Prepare top tags data for bar chart
  const tagsData = (stats.top_tags || []).slice(0, 10).map(tag => ({
    name: tag.tag,
    count: tag.count,
  }));

  // Prepare art styles data for bar chart
  const stylesData = (stats.top_art_styles || []).slice(0, 10).map(style => ({
    name: style.style,
    count: style.count,
  }));

  // Colors for charts
  const COLORS = ['#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6', '#ec4899'];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* NSFW Distribution Pie Chart */}
      {nsfwData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-slate-800 rounded-lg p-6 border border-slate-700"
        >
          <h3 className="text-xl font-semibold text-white mb-4">
            Distribución NSFW
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={nsfwData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {nsfwData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #475569',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      )}

      {/* Top Tags Bar Chart */}
      {tagsData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-slate-800 rounded-lg p-6 border border-slate-700"
        >
          <h3 className="text-xl font-semibold text-white mb-4">
            Top 10 Tags
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={tagsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis 
                dataKey="name" 
                stroke="#94a3b8" 
                angle={-45}
                textAnchor="end"
                height={100}
              />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #475569',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Bar dataKey="count" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      )}

      {/* Top Art Styles Bar Chart */}
      {stylesData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-slate-800 rounded-lg p-6 border border-slate-700 lg:col-span-2"
        >
          <h3 className="text-xl font-semibold text-white mb-4">
            Top 10 Estilos de Arte
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stylesData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis type="number" stroke="#94a3b8" />
              <YAxis 
                type="category" 
                dataKey="name" 
                stroke="#94a3b8"
                width={150}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #475569',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      )}
    </div>
  );
};
