import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Plus, UserPlus, Users } from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../auth';
import type { Project, User } from '../types';

export default function Projects() {
  const { user } = useAuth();
  const [items, setItems] = useState<Project[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [projectOpen, setProjectOpen] = useState(false);
  const [memberOpen, setMemberOpen] = useState(false);
  const projectForm = useForm<any>();
  const memberForm = useForm<any>();
  const load = () => api.get('/projects').then(response => setItems(response.data));
  const loadUsers = () => api.get('/users').then(response => setUsers(response.data));

  useEffect(() => {
    load();
    if (user?.role === 'admin') loadUsers();
  }, [user]);

  const saveProject = async (values: any) => {
    try {
      await api.post('/projects', { ...values, member_ids: (values.member_ids || []).map(Number) });
      toast.success('Project created');
      projectForm.reset();
      setProjectOpen(false);
      load();
    } catch (error: any) { toast.error(error.response?.data?.detail || 'Unable to create project'); }
  };
  const addMember = async (values: any) => {
    try {
      await api.post('/users', values);
      toast.success('Member account created');
      memberForm.reset();
      setMemberOpen(false);
      loadUsers();
    } catch (error: any) { toast.error(error.response?.data?.detail || 'Unable to add member'); }
  };
  const remove = async (id: number) => {
    if (!confirm('Delete this project and its tasks?')) return;
    await api.delete(`/projects/${id}`);
    toast.success('Project deleted');
    load();
  };

  return <>
    <div className="page-title"><div><h1>Projects</h1><p>Plan work and keep your team aligned.</p></div>
      {user?.role === 'admin' && <div className="actions"><button className="secondary" onClick={() => setMemberOpen(true)}><UserPlus size={18} /> Add member</button><button className="primary" onClick={() => setProjectOpen(true)}><Plus size={18} /> New project</button></div>}
    </div>
    <section className="project-grid">{items.map(project => <article className="project-card" key={project.id}><div className="project-top"><span className="folder"><Users size={18} /></span>{user?.role === 'admin' && <button className="text-danger" onClick={() => remove(project.id)}>Delete</button>}</div><h3>{project.name}</h3><p>{project.description || 'No description provided.'}</p><div className="avatars">{project.members.slice(0, 4).map(member => <span title={member.name} key={member.id}>{member.name[0]}</span>)}<small>{project.members.length} members</small></div></article>)}{!items.length && <p>No projects yet.</p>}</section>
    {user?.role === 'admin' && <section className="panel"><h3>All members</h3><div className="table-wrap"><table><thead><tr><th>Name</th><th>Email</th><th>Role</th></tr></thead><tbody>{users.map(member => <tr key={member.id}><td>{member.name}</td><td>{member.email}</td><td><span className="badge">{member.role}</span></td></tr>)}</tbody></table></div></section>}
    {projectOpen && <div className="modal-bg"><form className="modal" onSubmit={projectForm.handleSubmit(saveProject)}><div className="modal-title"><h2>New project</h2><button type="button" onClick={() => setProjectOpen(false)}>×</button></div><label>Name<input {...projectForm.register('name', { required: true })} /></label><label>Description<textarea {...projectForm.register('description')} /></label><label>Team members<select multiple {...projectForm.register('member_ids')}>{users.map(member => <option value={member.id} key={member.id}>{member.name} — {member.email}</option>)}</select><small>Hold Ctrl/Cmd to select multiple.</small></label><button className="primary">Create project</button></form></div>}
    {memberOpen && <div className="modal-bg"><form className="modal" onSubmit={memberForm.handleSubmit(addMember)}><div className="modal-title"><h2>Add member</h2><button type="button" onClick={() => setMemberOpen(false)}>×</button></div><label>Name<input {...memberForm.register('name', { required: true, minLength: 2 })} /></label><label>Email<input type="email" {...memberForm.register('email', { required: true })} /></label><label>Initial password<input type="password" minLength={8} {...memberForm.register('password', { required: true, minLength: 8 })} /><small>Use at least 8 characters. This account is created as a Member.</small></label><button className="primary">Create member</button></form></div>}
  </>;
}
