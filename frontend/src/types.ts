export type Role='admin'|'member'; export type Status='Todo'|'In Progress'|'Completed'; export type Priority='Low'|'Medium'|'High';
export interface User {id:number;name:string;email:string;role:Role;created_at:string}
export interface Project {id:number;name:string;description?:string;created_by:number;created_at:string;members:User[]}
export interface Task {id:number;title:string;description?:string;status:Status;priority:Priority;due_date?:string;assigned_to?:number;project_id:number;created_at:string;assignee?:User;project?:Project}
export interface Dashboard {total_projects:number;total_tasks:number;completed:number;todo:number;in_progress:number;overdue:number;upcoming:Task[];recent:Task[]}
