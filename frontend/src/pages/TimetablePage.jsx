import React, { useState, useEffect } from 'react';
import { 
  Calendar as CalendarIcon, Clock, MapPin, User, Users, 
  Filter, AlertCircle, CheckCircle2, ChevronRight, Sparkles 
} from 'lucide-react';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';

export const TimetablePage = ({ schedules = [], filters = {}, onRefresh }) => {
  const [selectedDay, setSelectedDay] = useState('Monday');
  const [selectedDept, setSelectedDept] = useState('');
  const [selectedRoom, setSelectedRoom] = useState('');
  const [selectedFaculty, setSelectedFaculty] = useState('');
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [activeSchedule, setActiveSchedule] = useState(null);

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  // Filter schedules
  const filteredSchedules = schedules.filter(s => {
    if (selectedDay && s.day_of_week !== selectedDay) return false;
    if (selectedRoom && s.room_id !== parseInt(selectedRoom)) return false;
    if (selectedFaculty && s.faculty_id !== parseInt(selectedFaculty)) return false;
    return true;
  });

  const handleOpenDetail = (sch) => {
    setActiveSchedule(sch);
    setDetailModalOpen(true);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header & Day Tabs */}
      <div className="bg-campus-card/90 border border-campus-border rounded-2xl p-5 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <CalendarIcon className="w-5 h-5 text-sky-400" />
              Campus Master Timetable
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Multi-department schedule grid with real-time autonomous disruption updates and room allocations.
            </p>
          </div>

          {/* Quick Stats */}
          <div className="flex items-center gap-3">
            <span className="text-xs px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-mono">
              Total Classes: <strong className="text-white">{filteredSchedules.length}</strong>
            </span>
          </div>
        </div>

        {/* Day Selectors */}
        <div className="flex flex-wrap items-center gap-2 pt-4">
          {days.map((day) => (
            <button
              key={day}
              onClick={() => setSelectedDay(day)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all-200 ${
                selectedDay === day
                  ? 'bg-sky-500 text-slate-950 font-bold shadow-md shadow-sky-500/20'
                  : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
              }`}
            >
              {day}
            </button>
          ))}
        </div>

        {/* Filters Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 mt-4 border-t border-slate-800/60">
          <div>
            <label className="text-[10px] uppercase font-mono font-bold text-slate-400 mb-1 block">Filter by Room</label>
            <select
              value={selectedRoom}
              onChange={(e) => setSelectedRoom(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Campus Rooms</option>
              {(filters.rooms || []).map((r) => (
                <option key={r.id} value={r.id}>{r.code} - {r.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[10px] uppercase font-mono font-bold text-slate-400 mb-1 block">Filter by Faculty</label>
            <select
              value={selectedFaculty}
              onChange={(e) => setSelectedFaculty(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Faculty</option>
              {(filters.faculties || []).map((f) => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => { setSelectedRoom(''); setSelectedFaculty(''); }}
              className="w-full py-2 px-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 text-xs text-slate-400 hover:text-white transition"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>

      {/* Timetable Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSchedules.length === 0 ? (
          <div className="col-span-full py-16 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-xs">
            No scheduled lectures or laboratories found for the selected day and filters.
          </div>
        ) : (
          filteredSchedules.map((sch) => {
            const isRescheduled = sch.status === 'Rescheduled';
            const isDisrupted = sch.status === 'Disrupted';

            return (
              <div
                key={sch.id}
                onClick={() => handleOpenDetail(sch)}
                className={`bg-campus-card/95 border rounded-2xl p-5 shadow-lg transition-all-200 cursor-pointer hover:border-sky-500/50 hover:shadow-sky-500/5 flex flex-col justify-between ${
                  isRescheduled ? 'border-amber-500/40 bg-amber-950/10' :
                  isDisrupted ? 'border-rose-500/40 bg-rose-950/10' : 'border-campus-border'
                }`}
              >
                <div>
                  {/* Top Bar with Time & Status */}
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-mono font-bold text-sky-400 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5" />
                      {sch.start_time} - {sch.end_time}
                    </span>

                    <Badge variant={
                      isRescheduled ? 'warning' :
                      isDisrupted ? 'danger' : 'success'
                    }>
                      {isRescheduled && <Sparkles className="w-3 h-3" />}
                      <span>{sch.status}</span>
                    </Badge>
                  </div>

                  {/* Course Details */}
                  <h4 className="text-sm font-bold text-white tracking-wide">{sch.course_name}</h4>
                  <p className="text-xs font-mono text-slate-400 mt-0.5">{sch.course_code}</p>

                  {/* Meta Tags */}
                  <div className="mt-4 space-y-2 text-xs text-slate-300">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span className="font-semibold text-white">{sch.room_code}</span>
                      <span className="text-slate-500 font-normal">({sch.building})</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <User className="w-3.5 h-3.5 text-slate-500" />
                      <span>{sch.faculty_name}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <Users className="w-3.5 h-3.5 text-slate-500" />
                      <span className="font-mono text-slate-300">{sch.cohort_code}</span>
                      <span className="text-slate-500">({sch.cohort_size} students)</span>
                    </div>
                  </div>
                </div>

                {/* Footer equipment chips */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {(sch.required_equipment || []).slice(0, 2).map((eq, idx) => (
                      <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                        {eq}
                      </span>
                    ))}
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-500" />
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Schedule Detail Modal */}
      <Modal
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        title={activeSchedule ? `${activeSchedule.course_code}: ${activeSchedule.course_name}` : 'Schedule Detail'}
      >
        {activeSchedule && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-slate-950/60 border border-slate-800">
              <div>
                <p className="text-[10px] font-mono uppercase text-slate-500">Day & Time Window</p>
                <p className="text-sm font-bold text-sky-400 mt-0.5">{activeSchedule.day_of_week}, {activeSchedule.start_time} - {activeSchedule.end_time}</p>
              </div>
              <div>
                <p className="text-[10px] font-mono uppercase text-slate-500">Timetable Status</p>
                <div className="mt-0.5">
                  <Badge variant={activeSchedule.status === 'Rescheduled' ? 'warning' : 'success'}>
                    {activeSchedule.status}
                  </Badge>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Facility & Hardware</h5>
              <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-800 text-xs space-y-1.5">
                <p><strong className="text-white">Assigned Facility:</strong> {activeSchedule.room_code} - {activeSchedule.room_name}</p>
                <p><strong className="text-white">Building:</strong> {activeSchedule.building}</p>
                <p><strong className="text-white">Cohort Enrollment:</strong> {activeSchedule.cohort_code} ({activeSchedule.cohort_size} Students)</p>
                <p><strong className="text-white">Faculty Instructor:</strong> {activeSchedule.faculty_name}</p>
              </div>
            </div>

            <div className="space-y-2">
              <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Required Infrastructure</h5>
              <div className="flex flex-wrap gap-1.5">
                {(activeSchedule.required_equipment || []).map((eq, i) => (
                  <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-sky-950/60 text-sky-300 border border-sky-800/40 font-mono">
                    {eq}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TimetablePage;
