import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, MapPin, Calendar, Loader2 } from 'lucide-react';
import { getIncidents } from '../api';

const severityStyles = {
  critical: 'bg-red-100 text-red-700',
  high: 'bg-amber-100 text-amber-700',
  medium: 'bg-blue-100 text-blue-700',
  low: 'bg-gray-100 text-gray-600',
};

const statusStyles = {
  open: 'bg-red-100 text-red-700',
  investigating: 'bg-amber-100 text-amber-700',
  resolved: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-600',
};

const categories = [
  { value: '', label: 'All Categories' },
  { value: 'theft', label: 'Theft' },
  { value: 'vandalism', label: 'Vandalism' },
  { value: 'suspicious_activity', label: 'Suspicious Activity' },
  { value: 'accident', label: 'Accident' },
  { value: 'noise_complaint', label: 'Noise Complaint' },
  { value: 'fire', label: 'Fire' },
  { value: 'flooding', label: 'Flooding' },
  { value: 'assault', label: 'Assault' },
  { value: 'other', label: 'Other' },
];

const statuses = [
  { value: '', label: 'All Statuses' },
  { value: 'open', label: 'Open' },
  { value: 'investigating', label: 'Investigating' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
];

export default function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchIncidents();
  }, [categoryFilter, statusFilter]);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const params = {};
      if (categoryFilter) params.category = categoryFilter;
      if (statusFilter) params.status = statusFilter;
      const res = await getIncidents(params);
      setIncidents(res.data.incidents || res.data || []);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load incidents');
    } finally {
      setLoading(false);
    }
  };

  const filteredIncidents = incidents.filter((inc) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      inc.title?.toLowerCase().includes(q) ||
      inc.description?.toLowerCase().includes(q) ||
      inc.location?.toLowerCase().includes(q)
    );
  });

  const formatCategory = (cat) => {
    if (!cat) return '';
    return cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Incidents</h1>
        <Link
          to="/report"
          className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-600 transition-colors"
        >
          + Report Incident
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search incidents..."
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex gap-3">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="pl-10 pr-8 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
            >
              {statuses.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          <span className="ml-2 text-sm text-gray-500">Loading incidents...</span>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg text-sm">{error}</div>
      ) : filteredIncidents.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-gray-500 text-sm">No incidents found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredIncidents.map((incident) => (
            <Link
              key={incident.id || incident._id}
              to={`/incidents/${incident.id || incident._id}`}
              className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-2 mb-3">
                <h3 className="text-sm font-semibold text-gray-800 line-clamp-1">
                  {incident.title}
                </h3>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-medium shrink-0 ${
                    severityStyles[incident.severity] || severityStyles.low
                  }`}
                >
                  {incident.severity}
                </span>
              </div>

              <div className="flex flex-wrap gap-2 mb-3">
                <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs font-medium">
                  {formatCategory(incident.category)}
                </span>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    statusStyles[incident.status] || statusStyles.open
                  }`}
                >
                  {incident.status}
                </span>
              </div>

              <p className="text-xs text-gray-500 line-clamp-2 mb-3">{incident.description}</p>

              <div className="flex items-center justify-between text-xs text-gray-400">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {incident.location || 'Unknown'}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {new Date(incident.created_at || incident.createdAt).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
