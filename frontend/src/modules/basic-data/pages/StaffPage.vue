<template>
  <div class="staff-page">
    <div class="page-header">
      <h1>Staff</h1>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">New Staff</el-button>
    </div>

    <div class="stats-container">
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">Total Staff</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.active }}</div>
        <div class="stat-label">Active</div>
      </el-card>
    </div>

    <el-card>
      <div class="table-controls">
        <el-input
          v-model="searchQuery"
          :prefix-icon="Search"
          placeholder="Search name or number"
          clearable
          style="width: 280px"
        />
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 180px">
          <el-option label="All" value="" />
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
      </div>

      <el-table :data="filteredStaff" v-loading="loading" style="width: 100%; margin-top: 16px">
        <el-table-column prop="number" label="Number" width="130" sortable />
        <el-table-column prop="name" label="Name" min-width="160" />
        <el-table-column prop="surname" label="Surname" min-width="160" />
        <el-table-column prop="email" label="Email" min-width="220" />
        <el-table-column prop="phone" label="Phone" width="150" />
        <el-table-column label="Status" width="140">
          <template #default="{ row }">
            <el-switch v-model="row.active" @change="toggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200">
          <template #default="{ row }">
            <el-button size="small" :icon="Edit" @click="openEditDialog(row)">Edit</el-button>
            <el-button size="small" type="danger" :icon="Delete" @click="deleteStaffMember(row)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="dialogMode === 'create' ? 'Create Staff' : 'Edit Staff'" width="520px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="140px">
        <el-form-item label="Number" prop="number">
          <el-input v-model="form.number" />
        </el-form-item>
        <el-form-item label="Name" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Surname" prop="surname">
          <el-input v-model="form.surname" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="Active">
          <el-switch v-model="form.active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          {{ dialogMode === 'create' ? 'Create' : 'Update' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue';
import { getStaff, createStaff, updateStaff, deleteStaff } from '@/modules/basic-data/services/basicDataService';

const staff = ref([]);
const loading = ref(false);
const submitting = ref(false);
const showDialog = ref(false);
const dialogMode = ref('create');
const searchQuery = ref('');
const statusFilter = ref('');
const formRef = ref(null);

const form = reactive({
  id: null,
  number: '',
  name: '',
  surname: '',
  email: '',
  phone: '',
  active: true,
});

const rules = {
  number: [{ required: true, message: 'Number is required', trigger: 'blur' }],
  name: [{ required: true, message: 'Name is required', trigger: 'blur' }],
  surname: [{ required: true, message: 'Surname is required', trigger: 'blur' }],
};

const stats = reactive({ total: 0, active: 0 });

const normalizeList = (payload) => {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.results)) return payload.results;
  return [];
};

const filteredStaff = computed(() => {
  let list = staff.value;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(s =>
      s.number.toLowerCase().includes(q) ||
      s.name.toLowerCase().includes(q) ||
      s.surname.toLowerCase().includes(q)
    );
  }
  if (statusFilter.value === 'active') {
    list = list.filter(s => s.active);
  } else if (statusFilter.value === 'inactive') {
    list = list.filter(s => !s.active);
  }
  return list;
});

const loadStaff = async () => {
  loading.value = true;
  try {
    staff.value = normalizeList(await getStaff());
    stats.total = staff.value.length;
    stats.active = staff.value.filter(s => s.active).length;
  } catch (error) {
    ElMessage.error('Failed to load staff');
  } finally {
    loading.value = false;
  }
};

const openCreateDialog = () => {
  dialogMode.value = 'create';
  resetForm();
  showDialog.value = true;
};

const openEditDialog = (entry) => {
  dialogMode.value = 'edit';
  Object.assign(form, {
    id: entry.id,
    number: entry.number,
    name: entry.name,
    surname: entry.surname,
    email: entry.email || '',
    phone: entry.phone || '',
    active: entry.active,
  });
  showDialog.value = true;
};

const resetForm = () => {
  Object.assign(form, {
    id: null,
    number: '',
    name: '',
    surname: '',
    email: '',
    phone: '',
    active: true,
  });
  formRef.value?.clearValidate();
};

const submitForm = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return;
    submitting.value = true;
    try {
      const payload = { ...form };
      if (dialogMode.value === 'create') {
        await createStaff(payload);
        ElMessage.success('Staff created');
      } else {
        await updateStaff(form.id, payload);
        ElMessage.success('Staff updated');
      }
      showDialog.value = false;
      await loadStaff();
    } catch (error) {
      ElMessage.error('Failed to save staff');
    } finally {
      submitting.value = false;
    }
  });
};

const toggleActive = async (entry) => {
  try {
    await updateStaff(entry.id, { active: entry.active });
    stats.active = staff.value.filter(s => s.active).length;
  } catch (error) {
    entry.active = !entry.active;
    ElMessage.error('Failed to update status');
  }
};

const deleteStaffMember = async (entry) => {
  try {
    await ElMessageBox.confirm(`Delete staff "${entry.name} ${entry.surname}"?`, 'Confirm', { type: 'warning' });
    await deleteStaff(entry.id);
    ElMessage.success('Staff deleted');
    await loadStaff();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete staff');
    }
  }
};

onMounted(() => {
  loadStaff();
});
</script>

<style scoped>
.staff-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 16px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
}

.stat-label {
  color: #909399;
}

.table-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
