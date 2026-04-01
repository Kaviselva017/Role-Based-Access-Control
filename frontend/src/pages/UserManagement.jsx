import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/UserManagement.css';

const UserManagement = () => {
  const { token } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingUserId, setEditingUserId] = useState(null);
  const [editFormData, setEditFormData] = useState({});
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'employee',
    department: ''
  });

  useEffect(() => {
    loadUsers();
    loadRoles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadUsers = async () => {
    try {
      const response = await fetch('/api/users', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
      } else {
        setError('Failed to load users');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadRoles = async () => {
    try {
      const response = await fetch('/api/roles');
      if (response.ok) {
        const data = await response.json();
        setRoles(data.roles);
      }
    } catch (err) {
      console.error('Failed to load roles:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setFormData({
          username: '',
          email: '',
          password: '',
          role: 'employee',
          department: ''
        });
        setShowAddForm(false);
        loadUsers();
      } else {
        const data = await response.json();
        setError(data.message);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        const response = await fetch(`/api/users/${userId}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.ok) {
          loadUsers();
        } else {
          setError('Failed to delete user');
        }
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const handleUpdateUserRole = async (userId, newRole) => {
    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ role: newRole })
      });

      if (response.ok) {
        loadUsers();
      } else {
        setError('Failed to update user role');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEditClick = (user) => {
    setEditingUserId(user.id);
    setEditFormData({
      username: user.username,
      email: user.email,
      department: user.department || '',
      role: user.role
    });
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditFormData({ ...editFormData, [name]: value });
  };

  const handleSaveEdit = async (userId) => {
    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(editFormData)
      });

      if (response.ok) {
        setEditingUserId(null);
        loadUsers();
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to update user');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div className="loading">Loading users...</div>;
  }

  return (
    <div className="user-management-container">
      <div className="management-header">
        <h1>USER MANAGEMENT</h1>
        <button
          className="add-user-btn"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? '✕ CANCEL' : '+ ADD USER'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showAddForm && (
        <div className="add-user-form">
          <h2>Add New User</h2>
          <form onSubmit={handleAddUser}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Role</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleInputChange}
              >
                {roles.map((role) => (
                  <option key={role.key} value={role.key}>
                    {role.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Department</label>
              <input
                type="text"
                name="department"
                value={formData.department}
                onChange={handleInputChange}
              />
            </div>

            <button type="submit" className="form-submit-btn">
              CREATE USER
            </button>
          </form>
        </div>
      )}

      <div className="users-table">
        <table>
          <thead>
            <tr>
              <th>USERNAME</th>
              <th>EMAIL</th>
              <th>ROLE</th>
              <th>DEPARTMENT</th>
              <th>LAST LOGIN</th>
              <th>CREATED</th>
              <th>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => {
              const isEditing = editingUserId === user.id;
              return (
                <tr key={user.id} className={isEditing ? 'editing-row' : ''}>
                  <td className="username-cell">
                    {isEditing ? (
                      <input 
                        type="text" 
                        name="username" 
                        value={editFormData.username} 
                        onChange={handleEditChange} 
                        className="edit-input"
                      />
                    ) : (
                      user.username
                    )}
                  </td>
                  <td>
                    {isEditing ? (
                      <input 
                        type="email" 
                        name="email" 
                        value={editFormData.email} 
                        onChange={handleEditChange} 
                        className="edit-input"
                      />
                    ) : (
                      user.email
                    )}
                  </td>
                  <td>
                    {isEditing ? (
                      <select name="role" value={editFormData.role} onChange={handleEditChange} className="edit-select">
                        {roles.map(r => <option key={r.key} value={r.key}>{r.name}</option>)}
                      </select>
                    ) : (
                      <select
                        value={user.role}
                        onChange={(e) => handleUpdateUserRole(user.id, e.target.value)}
                        className="role-select"
                      >
                        {roles.map((role) => (
                          <option key={role.key} value={role.key}>
                            {role.name}
                          </option>
                        ))}
                      </select>
                    )}
                  </td>
                  <td>
                    {isEditing ? (
                      <input 
                        type="text" 
                        name="department" 
                        value={editFormData.department} 
                        onChange={handleEditChange} 
                        className="edit-input"
                      />
                    ) : (
                      user.department || '-'
                    )}
                  </td>
                  <td className="date-cell">
                    {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="date-cell">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="actions-cell">
                    {isEditing ? (
                      <>
                        <button className="save-btn" onClick={() => handleSaveEdit(user.id)}>SAVE</button>
                        <button className="cancel-btn" onClick={() => setEditingUserId(null)}>CANCEL</button>
                      </>
                    ) : (
                      <>
                        <button className="edit-btn" onClick={() => handleEditClick(user)}>EDIT</button>
                        <button className="delete-btn" onClick={() => handleDeleteUser(user.id)}>DELETE</button>
                      </>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UserManagement;
