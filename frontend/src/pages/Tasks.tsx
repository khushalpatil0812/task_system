import { useEffect, useState } from 'react';
import { Plus, Search, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../api';
import { useAuth } from '../auth';
import TaskModal from '../components/TaskModal';
import type { Project, Task, User } from '../types';

export default function Tasks() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [selected, setSelected] = useState<Task>();
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState('');
  const [status, setStatus] = useState('');
  const load = () => api.get('/tasks', { params: { search: q || undefined, status_filter: status || undefined } }).then(response => setTasks(response.data));

  useEffect(() => { load(); }, [q, status]);
  useEffect(() => {
    api.get('/projects').then(response => setProjects(response.data));
    if (user?.role === 'admin') api.get('/users').then(response => setUsers(response.data));
    else setUsers(user ? [user] : []);
  }, [user]);

  const remove = async (id: number) => {
    if (!confirm('Delete this task?')) return;
    await api.delete(`/tasks/${id}`);
    toast.success('Task deleted');
    load();
  };
  const updateStatus = async (task: Task, newStatus: string) => {
    try {
      await api.put(`/tasks/${task.id}`, { status: newStatus });
      toast.success('Status updated');
      load();
    } catch {
      toast.error('Only an admin or the assigned member can update this task');
    }
  };

  return <>
    <div className="page-title"><div><h1>Tasks</h1><p>Track, prioritize, and complete work.</p></div>
      {user?.role === 'admin' && <button className="primary" onClick={() => { setSelected(undefined); setOpen(true); }}><Plus size={18} /> Create task</button>}
    </div>
    <div className="filters"><label className="search"><Search size={18} /><input placeholder="Search tasks..." value={q} onChange={event => setQ(event.target.value)} /></label>
      <select value={status} onChange={event => setStatus(event.target.value)}><option value="">All statuses</option><option>Todo</option><option>In Progress</option><option>Completed</option></select>
    </div>
    <section className="panel"><div className="table-wrap"><table><thead><tr><th>Task</th><th>Priority</th><th>Project</th><th>Assignee</th><th>Due date</th><th>Status</th><th /></tr></thead><tbody>
      {tasks.map(task => {
        const canUpdateStatus = user?.role === 'admin' || task.assigned_to === user?.id;
        return <tr key={task.id}><td><b>{task.title}</b><small>{task.description}</small></td><td><span className={`priority ${task.priority.toLowerCase()}`}>{task.priority}</span></td><td>{task.project?.name}</td><td>{task.assignee?.name || '—'}</td><td>{task.due_date || '—'}</td>
          <td><select className="status-select" value={task.status} disabled={!canUpdateStatus} title={canUpdateStatus ? '' : 'Only the assigned member can update this task'} onChange={event => updateStatus(task, event.target.value)}><option>Todo</option><option>In Progress</option><option>Completed</option></select></td>
          <td>{user?.role === 'admin' && <span className="actions"><button onClick={() => { setSelected(task); setOpen(true); }}>Edit</button><button className="text-danger" onClick={() => remove(task.id)}><Trash2 size={16} /></button></span>}</td>
        </tr>;
      })}
    </tbody></table></div></section>
    {open && <TaskModal task={selected} projects={projects} users={users} onClose={() => setOpen(false)} onSaved={load} />}
  </>;
}
