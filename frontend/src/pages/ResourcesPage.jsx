import React, { useState } from 'react';
import { 
  Building2, Search, Filter, CheckCircle2, AlertCircle, 
  Wrench, Users, Layers, ShieldCheck, Edit3 
} from 'lucide-react';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';

export const ResourcesPage = ({ resources = [], onUpdateResource }) => {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [buildingFilter, setBuildingFilter] = useState('');
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState(null);

  // Form state
  const [editForm, setEditForm] = useState({
    capacity: 40,
    is_available: true,
    maintenance_notes: ''
  });

  const roomTypes = Array.from(new Set(resources.map(r => r.room_type)));
  const buildings = Array.from(new Set(resources.map(r => r.building)));

  const filtered = resources.filter(r => {
    if (typeFilter && r.room_type !== typeFilter) return false;
    if (buildingFilter && r.building !== buildingFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      return r.code.toLowerCase().includes(q) || r.name.toLowerCase().includes(q) || r.building.toLowerCase().includes(q);
    }
    return true;
  });

  const handleOpenEdit = (room) => {
    setSelectedRoom(room);
    setEditForm({
      capacity: room.capacity,
      is_available: room.is_available,
      maintenance_notes: room.maintenance_notes || ''
    });
    setEditModalOpen(true);
  };

  const handleSaveEdit = async () => {
    if (!selectedRoom) return;
    await onUpdateResource(selectedRoom.id, editForm);
    setEditModalOpen(false);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Banner & Search Controls */}
      <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Building2 className="w-5 h-5 text-sky-400" />
              Campus Facilities & Infrastructure Directory
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Live capacity limits, GPU workstation availability, hardware equipment inventory, and maintenance states.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-mono">
              Total Facilities: <strong className="text-white">{filtered.length}</strong>
            </span>
          </div>
        </div>

        {/* Filter Toolbar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search code, lab name, building..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Facility Types</option>
              {roomTypes.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div>
            <select
              value={buildingFilter}
              onChange={(e) => setBuildingFilter(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Campus Buildings</option>
              {buildings.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Facilities Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((room) => (
          <div
            key={room.id}
            className="bg-campus-card/95 border border-campus-border hover:border-slate-700 rounded-2xl p-5 shadow-lg transition-all-200 flex flex-col justify-between"
          >
            <div>
              {/* Header */}
              <div className="flex items-start justify-between gap-3 mb-2">
                <div>
                  <span className="text-xs font-mono font-bold text-sky-400">{room.code}</span>
                  <h4 className="text-sm font-bold text-white tracking-wide mt-0.5">{room.name}</h4>
                </div>

                <Badge variant={room.is_available ? 'success' : 'danger'}>
                  {room.is_available ? 'Available' : 'Maintenance'}
                </Badge>
              </div>

              {/* Specs */}
              <div className="mt-3 space-y-1.5 text-xs text-slate-300">
                <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5" /> Building
                  </span>
                  <span className="font-medium text-white">{room.building} (Floor {room.floor})</span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5" /> Room Type
                  </span>
                  <span className="font-mono text-slate-200">{room.room_type}</span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Users className="w-3.5 h-3.5" /> Seating Capacity
                  </span>
                  <span className="font-mono font-bold text-white">{room.capacity} seats</span>
                </div>
              </div>

              {/* Equipment Tags */}
              <div className="mt-4">
                <p className="text-[10px] uppercase font-mono font-bold text-slate-500 mb-1.5">Equipped Hardware</p>
                <div className="flex flex-wrap gap-1">
                  {(room.equipment || []).map((eq, i) => (
                    <span 
                      key={i} 
                      className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                        eq.toLowerCase().includes('gpu') 
                          ? 'bg-sky-950 text-sky-300 border border-sky-800' 
                          : 'bg-slate-900 text-slate-400 border border-slate-800'
                      }`}
                    >
                      {eq}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Maintenance & Edit footer */}
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[10px] text-slate-500">
                {room.maintenance_notes ? `Note: ${room.maintenance_notes}` : 'Status nominal'}
              </span>
              <button
                onClick={() => handleOpenEdit(room)}
                className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-1 transition"
              >
                <Edit3 className="w-3 h-3 text-sky-400" />
                <span>Manage</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Edit Room Modal */}
      <Modal
        isOpen={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title={selectedRoom ? `Manage Facility: ${selectedRoom.code}` : 'Edit Facility'}
      >
        {selectedRoom && (
          <div className="space-y-4">
            <div>
              <label className="text-xs font-bold uppercase font-mono text-slate-400 mb-1 block">Capacity</label>
              <input
                type="number"
                value={editForm.capacity}
                onChange={(e) => setEditForm({ ...editForm, capacity: parseInt(e.target.value) || 0 })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="text-xs font-bold uppercase font-mono text-slate-400 mb-1 block">Operational Status</label>
              <select
                value={editForm.is_available ? 'true' : 'false'}
                onChange={(e) => setEditForm({ ...editForm, is_available: e.target.value === 'true' })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              >
                <option value="true">Available / Nominal</option>
                <option value="false">Under Maintenance / Unavailable</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-bold uppercase font-mono text-slate-400 mb-1 block">Maintenance Notes</label>
              <input
                type="text"
                placeholder="e.g. Scheduled electrical rewiring or projector servicing"
                value={editForm.maintenance_notes}
                onChange={(e) => setEditForm({ ...editForm, maintenance_notes: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>

            <div className="flex justify-end gap-2 pt-3">
              <button
                onClick={() => setEditModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-xs font-semibold text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-xs font-bold text-slate-950"
              >
                Save Changes
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ResourcesPage;
