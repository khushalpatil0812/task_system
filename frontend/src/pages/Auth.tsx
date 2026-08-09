import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { useAuth } from '../auth';

function AuthForm({ signup = false }: { signup?: boolean }) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<Record<string, string>>();
  const { login, signup: join } = useAuth(); const navigate = useNavigate();
  const submit = async (values: Record<string, string>) => { try { signup ? await join(values) : await login(values.email, values.password); toast.success(signup ? 'Account created' : 'Welcome back'); navigate('/'); } catch (error: any) { toast.error(error.response?.data?.detail || 'Something went wrong'); } };
  return <div className="auth"><form onSubmit={handleSubmit(submit)}><div className="auth-brand">Task<span>Flow</span></div><h1>{signup ? 'Create your workspace' : 'Welcome back'}</h1><p>{signup ? 'Start organizing your team today.' : 'Sign in to manage your team tasks.'}</p>{signup && <label>Name<input {...register('name', { required: 'Name is required', minLength: 2 })}/>{errors.name?.message}</label>}<label>Email<input type="email" {...register('email', { required: 'Email is required' })}/>{errors.email?.message}</label><label>Password<input type="password" {...register('password', { required: 'Password is required', minLength: 8 })}/>{errors.password?.message}</label><button className="primary" disabled={isSubmitting}>{isSubmitting ? 'Please wait…' : signup ? 'Create account' : 'Sign in'}</button><p className="switch">{signup ? 'Already have an account?' : 'New here?'} <Link to={signup ? '/login' : '/signup'}>{signup ? 'Sign in' : 'Create account'}</Link></p></form></div>;
}
export const Login = () => <AuthForm/>; export const Signup = () => <AuthForm signup/>;
