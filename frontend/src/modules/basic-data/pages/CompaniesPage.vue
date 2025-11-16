<template>
  <div class="companies-page">
    <div class="page-header">
      <h1>Companies</h1>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">New Company</el-button>
    </div>

    <div class="stats-container">
      <el-card class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">Total Companies</div>
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
          placeholder="Search by name or number"
          clearable
          style="width: 280px"
        />
        <el-select
          v-model="statusFilter"
          placeholder="Status"
          clearable
          style="width: 180px"
        >
          <el-option label="All" value="" />
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
      </div>

      <el-table :data="filteredCompanies" v-loading="loading" style="width: 100%; margin-top: 16px">
        <el-table-column prop="number" label="Number" width="130" sortable />
        <el-table-column prop="name" label="Name" min-width="200" sortable />
        <el-table-column prop="email" label="Email" min-width="200" />
        <el-table-column prop="phone" label="Phone" width="150" />
        <el-table-column prop="country" label="Country" width="140" />
        <el-table-column label="Status" width="140">
          <template #default="{ row }">
            <el-switch v-model="row.active" @change="toggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200">
          <template #default="{ row }">
            <el-button size="small" :icon="Edit" @click="openEditDialog(row)">Edit</el-button>
            <el-button size="small" type="danger" :icon="Delete" @click="deleteCompany(row)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="dialogMode === 'create' ? 'Create Company' : 'Edit Company'" width="560px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="140px">
        <el-form-item label="Number" prop="number">
          <el-input v-model="form.number" />
        </el-form-item>
        <el-form-item label="Name" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="City">
          <el-input v-model="form.city" />
        </el-form-item>
        <el-form-item label="Country">
          <el-input v-model="form.country" />
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
import { getCompanies, createCompany, updateCompany, deleteCompany as apiDeleteCompany } from '@/modules/basic-data/services/basicDataService';

const companies = ref([]);
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
  email: '',
  phone: '',
  city: '',
  country: '',
  active: true,
});

const rules = {
  number: [{ required: true, message: 'Number is required', trigger: 'blur' }],
  name: [{ required: true, message: 'Name is required', trigger: 'blur' }],
};

const stats = reactive({ total: 0, active: 0 });

const normalizeList = (payload) => {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.results)) return payload.results;
  return [];
};

const filteredCompanies = computed(() => {
  let list = companies.value;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(c =>
      c.number.toLowerCase().includes(q) ||
      c.name.toLowerCase().includes(q) ||
      (c.city && c.city.toLowerCase().includes(q))
    );
  }
  if (statusFilter.value === 'active') {
    list = list.filter(c => c.active);
  } else if (statusFilter.value === 'inactive') {
    list = list.filter(c => !c.active);
  }
  return list;
});

const loadCompanies = async () => {
  loading.value = true;
  try {
    companies.value = normalizeList(await getCompanies());
    stats.total = companies.value.length;
    stats.active = companies.value.filter(c => c.active).length;
  } catch (error) {
    ElMessage.error('Failed to load companies');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const openCreateDialog = () => {
  dialogMode.value = 'create';
  resetForm();
  showDialog.value = true;
};

const openEditDialog = (company) => {
  dialogMode.value = 'edit';
  Object.assign(form, {
    id: company.id,
    number: company.number,
    name: company.name,
    email: company.email || '',
    phone: company.phone || '',
    city: company.city || '',
    country: company.country || '',
    active: company.active,
  });
  showDialog.value = true;
};

const resetForm = () => {
  Object.assign(form, {
    id: null,
    number: '',
    name: '',
    email: '',
    phone: '',
    city: '',
    country: '',
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
        await createCompany(payload);
        ElMessage.success('Company created');
      } else {
        await updateCompany(form.id, payload);
        ElMessage.success('Company updated');
      }
      showDialog.value = false;
      await loadCompanies();
    } catch (error) {
      ElMessage.error('Failed to save company');
      console.error(error);
    } finally {
      submitting.value = false;
    }
  });
};

const toggleActive = async (company) => {
  try {
    await updateCompany(company.id, { active: company.active });
    stats.active = companies.value.filter(c => c.active).length;
  } catch (error) {
    company.active = !company.active;
    ElMessage.error('Failed to update status');
  }
};

const deleteCompany = async (company) => {
  try {
    await ElMessageBox.confirm(`Delete company "${company.name}"?`, 'Confirm', { type: 'warning' });
    await apiDeleteCompany(company.id);
    ElMessage.success('Company deleted');
    await loadCompanies();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete company');
    }
  }
};

onMounted(() => {
  loadCompanies();
});
</script>

<style scoped>
.companies-page {
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
