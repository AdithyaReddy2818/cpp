import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  MapPin,
  Calendar,
  User,
  Loader2,
  Trash2,
  Save,
  Pencil,
  X,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { getIncident, updateIncident, updateStatus, deleteIncident } from '../api';

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

const statusOptions = ['open', 'investigating', 'resolved', 'closed'];

export default function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newStatus, setNewStatus] = useState('');
  const [adminNotes, setAdminNotes] = useState('');
  const [updating, setUpdating] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({ title: '', description: '', category: '', location: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchIncident();
  }, [id]);

  const fetchIncident = async () => {
    try {
      const res = await getIncident(id);
      const data = res.data.incident || res.data;
      setIncident(data);
      setNewStatus(data.status || 'open');
      setAdminNotes(data.admin_notes || data.adminNotes || '');
      setEditForm({
        title: data.title || '',
        description: data.description || '',
        category: data.category || '',
        location: data.location || '',
      });
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load incident');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async () => {
    setUpdating(true);
    try {
      await updateStatus(id, { status: newStatus, admin_notes: adminNotes });
      toast.success('Status updated successfully');
      fetchIncident();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deleteIncident(id);
      toast.success('Incident deleted');
      navigate('/incidents');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to delete incident');
    } finally {
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleEditSave = async () => {
    setSaving(true);
    try {
      await updateIncident(id, editForm);
      toast.success('Incident updated successfully');
      setEditing(false);
      fetchIncident();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update incident');
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (value) => {
    if (!value) return 'Unknown';
    // If it looks like a unix timestamp in seconds (less than 10 billion), multiply by 1000
    const ts = typeof value === 'number' && value < 1e12 ? value * 1000 : value;
    const d = new Date(ts);
    if (isNaN(d.getTime())) return 'Unknown';
    return d.toLocaleString();
  };

  const formatCategory = (cat) => {
    if (!cat) return '';
    return cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="skeleton h-6 w-24 mb-6"></div>
        <div className="skeleton h-10 w-72 mb-4"></div>
        <div className="skeleton h-64 rounded-xl"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link to="/incidents" className="flex items-center gap-1 text-sm text-blue-600 hover:underline mb-4">
          <ArrowLeft className="w-4 h-4" /> Back to incidents
        </Link>
        <div className="bg-red-50 text-red-700 p-4 rounded-lg text-sm">{error}</div>
      </div>
    );
  }

  if (!incident) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link
        to="/incidents"
        className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline mb-6"
      >
        <ArrowLeft className="w-4 h-4" /> Back to incidents
      </Link>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        {editing ? (
          <div className="space-y-4 mb-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-semibold text-gray-800">Edit Incident</h2>
              <button
                onClick={() => setEditing(false)}
                className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                <X className="w-4 h-4" /> Cancel
              </button>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                type="text"
                value={editForm.title}
                onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                rows={4}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={editForm.category}
                  onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
                >
                  {['theft', 'vandalism', 'assault', 'suspicious_activity', 'noise_complaint', 'traffic', 'fire', 'environmental', 'other'].map((c) => (
                    <option key={c} value={c}>{formatCategory(c)}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input
                  type="text"
                  value={editForm.location}
                  onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <button
              onClick={handleEditSave}
              disabled={saving}
              className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        ) : (
        <>
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">{incident.title}</h1>
            <div className="flex flex-wrap gap-2">
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  severityStyles[incident.severity] || severityStyles.low
                }`}
              >
                {incident.severity}
              </span>
              <span className="bg-gray-100 text-gray-600 px-2.5 py-0.5 rounded-full text-xs font-medium">
                {formatCategory(incident.category)}
              </span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  statusStyles[incident.status] || statusStyles.open
                }`}
              >
                {incident.status}
              </span>
            </div>
          </div>
          <button
            onClick={() => setEditing(true)}
            className="flex items-center gap-2 border border-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            <Pencil className="w-4 h-4" /> Edit
          </button>
        </div>

        <div className="prose prose-sm max-w-none mb-6">
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{incident.description}</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span>{incident.location || 'Unknown location'}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <User className="w-4 h-4 text-gray-400" />
            <span>{incident.reportedByUsername || incident.reporter_name || incident.reporterName || 'Anonymous'}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span>
              {formatDate(incident.created_at || incident.createdAt)}
            </span>
          </div>
        </div>

        {(incident.latitude || incident.longitude) && (
          <div className="text-xs text-gray-400 mb-6">
            Coordinates: {incident.latitude}, {incident.longitude}
          </div>
        )}

        {(incident.image || incident.image_url || incident.imageUrl) && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Attached Image</h3>
            <img
              src={incident.image || incident.image_url || incident.imageUrl}
              alt="Incident"
              className="max-w-md rounded-lg border border-gray-200"
            />
          </div>
        )}
        </>
        )}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Update Status</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Status</label>
            <select
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              className="w-full sm:w-64 px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
            >
              {statusOptions.map((s) => (
                <option key={s} value={s}>
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Admin Notes</label>
            <textarea
              value={adminNotes}
              onChange={(e) => setAdminNotes(e.target.value)}
              placeholder="Add notes about this incident..."
              rows={3}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <button
            onClick={handleStatusUpdate}
            disabled={updating}
            className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {updating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {updating ? 'Updating...' : 'Update Status'}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-2">Danger Zone</h2>
        <p className="text-sm text-gray-500 mb-4">
          Permanently delete this incident. This action cannot be undone.
        </p>

        {showDeleteConfirm ? (
          <div className="flex items-center gap-3">
            <span className="text-sm text-red-600 font-medium">Are you sure?</span>
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="flex items-center gap-2 bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-600 disabled:opacity-50 transition-colors"
            >
              {deleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
              {deleting ? 'Deleting...' : 'Yes, delete'}
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="flex items-center gap-2 border border-red-200 text-red-600 px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            Delete Incident
          </button>
        )}
      </div>
    </div>
  );
}
