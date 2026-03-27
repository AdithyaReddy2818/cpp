import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  Search,
  CheckCircle,
  Clock,
  Bell,
  Loader2,
  ArrowRight,
  Mail,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { getDashboard, subscribe, getSubscriberCount } from '../api';

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

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [subEmail, setSubEmail] = useState('');
  const [subscribing, setSubscribing] = useState(false);
  const [subscriberCount, setSubscriberCount] = useState(0);

  useEffect(() => {
    fetchDashboard();
    fetchSubscriberCount();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await getDashboard();
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const fetchSubscriberCount = async () => {
    try {
      const res = await getSubscriberCount();
      setSubscriberCount(res.data.count || 0);
    } catch {
      // silent
    }
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    if (!subEmail) {
      toast.error('Please enter your email');
      return;
    }
    setSubscribing(true);
    try {
      await subscribe({ email: subEmail });
      toast.success('Subscribed to safety alerts!');
      setSubEmail('');
      fetchSubscriberCount();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to subscribe');
    } finally {
      setSubscribing(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="skeleton h-8 w-48 mb-8"></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-28 rounded-xl"></div>
          ))}
        </div>
        <div className="skeleton h-64 rounded-xl"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 text-red-700 p-4 rounded-lg text-sm">{error}</div>
      </div>
    );
  }

  const stats = data?.stats || {};
  const recentIncidents = data?.recent_incidents || [];

  const statCards = [
    {
      label: 'Total Incidents',
      value: stats.total || 0,
      icon: AlertTriangle,
      bg: 'bg-blue-50',
      iconColor: 'text-blue-600',
    },
    {
      label: 'Open',
      value: stats.open || 0,
      icon: Clock,
      bg: 'bg-red-50',
      iconColor: 'text-red-500',
    },
    {
      label: 'Investigating',
      value: stats.investigating || 0,
      icon: Search,
      bg: 'bg-amber-50',
      iconColor: 'text-amber-500',
    },
    {
      label: 'Resolved',
      value: stats.resolved || 0,
      icon: CheckCircle,
      bg: 'bg-green-50',
      iconColor: 'text-green-500',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Safety Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((card) => (
          <div
            key={card.label}
            className="bg-white rounded-xl border border-gray-200 p-5 flex items-center gap-4"
          >
            <div className={`${card.bg} p-3 rounded-lg`}>
              <card.icon className={`w-6 h-6 ${card.iconColor}`} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-800">{card.value}</p>
              <p className="text-sm text-gray-500">{card.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Recent Incidents</h2>
          <Link
            to="/incidents"
            className="flex items-center gap-1 text-sm text-blue-600 font-medium hover:underline"
          >
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {recentIncidents.length === 0 ? (
          <p className="text-sm text-gray-500 py-8 text-center">No incidents reported yet.</p>
        ) : (
          <div className="space-y-3">
            {recentIncidents.slice(0, 10).map((incident) => (
              <Link
                key={incident.id || incident._id}
                to={`/incidents/${incident.id || incident._id}`}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors border border-gray-100"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{incident.title}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {incident.location} &middot;{' '}
                    {new Date(incident.created_at || incident.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      severityStyles[incident.severity] || severityStyles.low
                    }`}
                  >
                    {incident.severity}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      statusStyles[incident.status] || statusStyles.open
                    }`}
                  >
                    {incident.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-blue-50 p-2 rounded-lg">
            <Bell className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-800">Safety Alerts</h2>
            <p className="text-sm text-gray-500">
              Get notified about incidents in your area.{' '}
              {subscriberCount > 0 && (
                <span className="text-blue-600 font-medium">{subscriberCount} subscribers</span>
              )}
            </p>
          </div>
        </div>
        <form onSubmit={handleSubscribe} className="flex gap-3">
          <div className="relative flex-1">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="email"
              value={subEmail}
              onChange={(e) => setSubEmail(e.target.value)}
              placeholder="Enter your email"
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            disabled={subscribing}
            className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {subscribing ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            Subscribe
          </button>
        </form>
      </div>
    </div>
  );
}
