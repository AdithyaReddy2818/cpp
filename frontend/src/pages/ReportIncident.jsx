import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, MapPin, Upload, Loader2, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { createIncident } from '../api';

const categories = [
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

const severities = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
];

export default function ReportIncident() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'theft',
    severity: 'medium',
    location: '',
    latitude: '',
    longitude: '',
    image: '',
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image must be under 5MB');
      return;
    }
    const reader = new FileReader();
    reader.onloadend = () => {
      setForm({ ...form, image: reader.result });
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const removeImage = () => {
    setForm({ ...form, image: '' });
    setImagePreview(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title || !form.description || !form.location) {
      toast.error('Please fill in required fields');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        title: form.title,
        description: form.description,
        category: form.category,
        severity: form.severity,
        location: form.location,
      };
      if (form.latitude) payload.latitude = parseFloat(form.latitude);
      if (form.longitude) payload.longitude = parseFloat(form.longitude);
      if (form.image) payload.image = form.image;

      const res = await createIncident(payload);
      const newId = res.data.id || res.data._id || res.data.incident?.id || res.data.incident?._id;
      toast.success('Incident reported successfully!');
      if (newId) {
        navigate(`/incidents/${newId}`);
      } else {
        navigate('/incidents');
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to report incident');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-red-50 p-2 rounded-lg">
          <AlertTriangle className="w-6 h-6 text-red-500" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Report an Incident</h1>
          <p className="text-sm text-gray-500">Help keep your neighbourhood safe</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="title"
              value={form.title}
              onChange={handleChange}
              placeholder="Brief title of the incident"
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              placeholder="Describe what happened in detail..."
              rows={4}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Category</label>
              <select
                name="category"
                value={form.category}
                onChange={handleChange}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Severity</label>
              <select
                name="severity"
                value={form.severity}
                onChange={handleChange}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
              >
                {severities.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" /> Location <span className="text-red-500">*</span>
              </span>
            </label>
            <input
              type="text"
              name="location"
              value={form.location}
              onChange={handleChange}
              placeholder="Street address or area name"
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Latitude <span className="text-gray-400 font-normal">(optional)</span>
              </label>
              <input
                type="number"
                step="any"
                name="latitude"
                value={form.latitude}
                onChange={handleChange}
                placeholder="e.g. 53.3498"
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Longitude <span className="text-gray-400 font-normal">(optional)</span>
              </label>
              <input
                type="number"
                step="any"
                name="longitude"
                value={form.longitude}
                onChange={handleChange}
                placeholder="e.g. -6.2603"
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Image <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            {imagePreview ? (
              <div className="relative inline-block">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="w-48 h-32 object-cover rounded-lg border border-gray-200"
                />
                <button
                  type="button"
                  onClick={removeImage}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ) : (
              <label className="flex items-center justify-center gap-2 w-full py-8 border-2 border-dashed border-gray-200 rounded-lg cursor-pointer hover:border-gray-300 transition-colors">
                <Upload className="w-5 h-5 text-gray-400" />
                <span className="text-sm text-gray-500">Click to upload an image</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="hidden"
                />
              </label>
            )}
          </div>
        </div>

        <div className="mt-8 flex items-center gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 bg-red-500 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-red-600 disabled:opacity-50 transition-colors"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <AlertTriangle className="w-4 h-4" />}
            {loading ? 'Submitting...' : 'Report Incident'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/incidents')}
            className="px-6 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
