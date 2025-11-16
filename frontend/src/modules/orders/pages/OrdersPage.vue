<template>
  <div class="orders-page">
    <!-- Header with Stats -->
    <div class="page-header">
      <h1>Orders Management</h1>
      <div class="stats-cards">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="Total Orders" :value="stats.total" />
        </el-card>
        <el-card shadow="hover" class="stat-card pending">
          <el-statistic title="Pending" :value="stats.pending" />
        </el-card>
        <el-card shadow="hover" class="stat-card in-progress">
          <el-statistic title="In Progress" :value="stats.in_progress" />
        </el-card>
        <el-card shadow="hover" class="stat-card completed">
          <el-statistic title="Completed" :value="stats.completed" />
        </el-card>
      </div>
    </div>
    
    <el-card>
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button 
            v-if="canManageOrders" 
            type="primary" 
            :icon="Plus"
            @click="showCreateDialog = true"
          >
            Create Order
          </el-button>
          <el-button 
            :icon="Refresh"
            @click="loadOrders"
          >
            Refresh
          </el-button>
          <el-button 
            v-if="canManageOrders && selectedRows.length > 0"
            :icon="Operation"
            @click="showBulkStateDialog = true"
          >
            Change State ({{ selectedRows.length }})
          </el-button>
        </div>
        
        <div class="toolbar-right">
          <el-input
            v-model="searchQuery"
            placeholder="Search by number, name..."
            style="width: 250px;"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select 
            v-model="filterState" 
            placeholder="State" 
            clearable
            @change="loadOrders" 
            style="margin-left: 10px; width: 150px;"
          >
            <el-option label="All States" value="" />
            <el-option label="Pending" value="pending" />
            <el-option label="Accepted" value="accepted" />
            <el-option label="In Progress" value="in_progress" />
            <el-option label="Completed" value="completed" />
            <el-option label="Declined" value="declined" />
            <el-option label="Interrupted" value="interrupted" />
            <el-option label="Abandoned" value="abandoned" />
          </el-select>
          
          <el-select 
            v-model="filterProductionLine" 
            placeholder="Production Line" 
            clearable
            filterable
            @change="loadOrders" 
            style="margin-left: 10px; width: 180px;"
          >
            <el-option label="All Lines" value="" />
            <el-option 
              v-for="line in productionLines" 
              :key="line.id" 
              :label="line.name" 
              :value="line.id" 
            />
          </el-select>
        </div>
      </div>

      <!-- Orders Table -->
      <el-table 
        :data="orders" 
        style="width: 100%; margin-top: 20px;" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        row-key="id"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="number" label="Order Number" width="140" sortable>
          <template #default="scope">
            <el-link type="primary" @click="viewOrderDetails(scope.row)">
              {{ scope.row.number }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="product_name" label="Product" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <div>
              <div class="product-name">{{ scope.row.product_name }}</div>
              <div class="product-number">{{ scope.row.product_number }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Quantity" width="140" align="center">
          <template #default="scope">
            <div class="quantity-info">
              <div>{{ scope.row.done_quantity }} / {{ scope.row.planned_quantity }}</div>
              <el-progress 
                :percentage="getProgressPercentage(scope.row)" 
                :status="getProgressStatus(scope.row)"
                :stroke-width="4"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="state" label="State" width="130">
          <template #default="scope">
            <el-tag :type="getStateType(scope.row.state)">
              {{ formatState(scope.row.state) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="production_line_name" label="Line" width="130" show-overflow-tooltip />
        <el-table-column prop="deadline" label="Deadline" width="160" sortable>
          <template #default="scope">
            <div v-if="scope.row.deadline" :class="getDeadlineClass(scope.row.deadline)">
              <el-icon><Clock /></el-icon>
              {{ formatDate(scope.row.deadline) }}
            </div>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button size="small" :icon="View" @click="viewOrderDetails(scope.row)">
                View
              </el-button>
              <el-dropdown v-if="canManageOrders" trigger="click" @command="handleOrderAction($event, scope.row)">
                <el-button size="small" :icon="More" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit" :icon="Edit">Edit</el-dropdown-item>
                    <el-dropdown-item command="state" :icon="Operation">Change State</el-dropdown-item>
                    <el-dropdown-item command="schedule" :icon="Calendar">Schedule</el-dropdown-item>
                    <el-dropdown-item command="copy" :icon="CopyDocument">Copy</el-dropdown-item>
                    <el-dropdown-item divided command="delete" :icon="Delete">Delete</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="loadOrders"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- Create/Edit Order Dialog -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingOrder ? 'Edit Order' : 'Create New Order'" 
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="orderForm" :rules="orderRules" ref="orderFormRef" label-width="160px">
        <el-form-item label="Order Number" prop="number">
          <el-input v-model="orderForm.number" placeholder="AUTO" />
          <span class="form-hint">Leave empty for auto-generation</span>
        </el-form-item>
        
        <el-form-item label="Order Name" prop="name">
          <el-input v-model="orderForm.name" />
        </el-form-item>
        
        <el-form-item label="External Number">
          <el-input v-model="orderForm.external_number" placeholder="Customer order number" />
        </el-form-item>
        
        <el-form-item label="Product" prop="product">
          <el-select 
            v-model="orderForm.product" 
            filterable 
            placeholder="Select Product" 
            style="width: 100%;"
            @change="handleProductChange"
          >
            <el-option 
              v-for="product in products" 
              :key="product.id" 
              :label="`${product.number} - ${product.name}`" 
              :value="product.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Routing">
          <el-select 
            v-model="orderForm.technology" 
            filterable 
            placeholder="Select routing" 
            style="width: 100%;"
            clearable
          >
            <el-option 
              v-for="tech in technologies" 
              :key="tech.id" 
              :label="`${tech.number} - ${tech.name}`" 
              :value="tech.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Production Line">
          <el-select 
            v-model="orderForm.production_line" 
            filterable 
            placeholder="Select Production Line" 
            style="width: 100%;"
            clearable
          >
            <el-option 
              v-for="line in productionLines" 
              :key="line.id" 
              :label="line.name" 
              :value="line.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Planned Quantity" prop="planned_quantity">
              <el-input-number 
                v-model="orderForm.planned_quantity" 
                :min="0.00001" 
                :precision="5" 
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Done Quantity">
              <el-input-number 
                v-model="orderForm.done_quantity" 
                :min="0" 
                :precision="5" 
                :disabled="!editingOrder"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="Deadline">
          <el-date-picker 
            v-model="orderForm.deadline" 
            type="datetime" 
            placeholder="Select deadline" 
            style="width: 100%;"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Date From">
              <el-date-picker 
                v-model="orderForm.date_from" 
                type="datetime" 
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Date To">
              <el-date-picker 
                v-model="orderForm.date_to" 
                type="datetime" 
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="Company">
          <el-select 
            v-model="orderForm.company" 
            filterable 
            placeholder="Select Company" 
            style="width: 100%;"
            clearable
          >
            <el-option 
              v-for="company in companies" 
              :key="company.id" 
              :label="company.name" 
              :value="company.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Description">
          <el-input 
            v-model="orderForm.description" 
            type="textarea" 
            :rows="4" 
            placeholder="Order description and notes..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveOrder" :loading="saving">
          {{ editingOrder ? 'Update' : 'Create' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Order Details Dialog -->
    <el-dialog 
      v-model="showDetailsDialog" 
      :title="'Order Details: ' + (selectedOrder?.number || '')" 
      width="900px"
    >
      <div v-if="selectedOrder" class="order-details">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="General" name="general">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Order Number">{{ selectedOrder.number }}</el-descriptions-item>
              <el-descriptions-item label="Order Name">{{ selectedOrder.name }}</el-descriptions-item>
              <el-descriptions-item label="External Number">
                {{ selectedOrder.external_number || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="State">
                <el-tag :type="getStateType(selectedOrder.state)">
                  {{ formatState(selectedOrder.state) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Product">
                {{ selectedOrder.product_name }} ({{ selectedOrder.product_number }})
              </el-descriptions-item>
              <el-descriptions-item label="Routing">
                {{ selectedOrder.technology_name || 'Not assigned' }}
              </el-descriptions-item>
              <el-descriptions-item label="Production Line">
                {{ selectedOrder.production_line_name || 'Not assigned' }}
              </el-descriptions-item>
              <el-descriptions-item label="Company">
                {{ selectedOrder.company_name || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="Planned Quantity">
                {{ selectedOrder.planned_quantity }}
              </el-descriptions-item>
              <el-descriptions-item label="Done Quantity">
                {{ selectedOrder.done_quantity }}
              </el-descriptions-item>
              <el-descriptions-item label="Progress">
                <el-progress 
                  :percentage="getProgressPercentage(selectedOrder)" 
                  :status="getProgressStatus(selectedOrder)"
                />
              </el-descriptions-item>
              <el-descriptions-item label="Deadline">
                {{ selectedOrder.deadline ? formatDateTime(selectedOrder.deadline) : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="Date From">
                {{ selectedOrder.date_from ? formatDateTime(selectedOrder.date_from) : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="Date To">
                {{ selectedOrder.date_to ? formatDateTime(selectedOrder.date_to) : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="Created">
                {{ formatDateTime(selectedOrder.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="Last Updated">
                {{ formatDateTime(selectedOrder.updated_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="Description" :span="2">
                {{ selectedOrder.description || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="State History" name="history">
            <el-timeline>
              <el-timeline-item 
                v-for="change in orderStateHistory" 
                :key="change.id"
                :timestamp="formatDateTime(change.date_and_time)"
                placement="top"
              >
                <el-card>
                  <p>
                    <el-tag :type="getStateType(change.source_state)" size="small">
                      {{ formatState(change.source_state) }}
                    </el-tag>
                    <el-icon style="margin: 0 8px;"><Right /></el-icon>
                    <el-tag :type="getStateType(change.target_state)" size="small">
                      {{ formatState(change.target_state) }}
                    </el-tag>
                  </p>
                  <p v-if="change.worker" class="worker-info">
                    <el-icon><User /></el-icon> {{ change.worker }}
                  </p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-if="orderStateHistory.length === 0" description="No state changes recorded" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- Change State Dialog -->
    <el-dialog 
      v-model="showStateDialog" 
      title="Change Order State" 
      width="450px"
    >
      <el-form label-width="120px">
        <el-form-item label="Current State">
          <el-tag :type="getStateType(stateChangeOrder?.state)">
            {{ formatState(stateChangeOrder?.state) }}
          </el-tag>
        </el-form-item>
        <el-form-item label="New State">
          <el-select v-model="newState" placeholder="Select new state" style="width: 100%;">
            <el-option label="Pending" value="pending" />
            <el-option label="Accepted" value="accepted" />
            <el-option label="In Progress" value="in_progress" />
            <el-option label="Completed" value="completed" />
            <el-option label="Declined" value="declined" />
            <el-option label="Interrupted" value="interrupted" />
            <el-option label="Abandoned" value="abandoned" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="changeOrderState" :loading="changingState">
          Change State
        </el-button>
      </template>
    </el-dialog>

    <!-- Bulk State Change Dialog -->
    <el-dialog 
      v-model="showBulkStateDialog" 
      title="Bulk Change State" 
      width="450px"
    >
      <el-alert 
        title="Bulk Operation" 
        :description="`Change state for ${selectedRows.length} selected orders`"
        type="info" 
        :closable="false"
        style="margin-bottom: 20px;"
      />
      <el-form label-width="120px">
        <el-form-item label="New State">
          <el-select v-model="bulkNewState" placeholder="Select new state" style="width: 100%;">
            <el-option label="Pending" value="pending" />
            <el-option label="Accepted" value="accepted" />
            <el-option label="In Progress" value="in_progress" />
            <el-option label="Completed" value="completed" />
            <el-option label="Declined" value="declined" />
            <el-option label="Interrupted" value="interrupted" />
            <el-option label="Abandoned" value="abandoned" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBulkStateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="bulkChangeState" :loading="changingState">
          Change State
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  Plus, Refresh, Search, View, Edit, Delete, More, Operation, 
  Calendar, CopyDocument, Clock, User, Right 
} from '@element-plus/icons-vue';
import { 
  getOrders, 
  createOrder, 
  updateOrder, 
  deleteOrder,
  changeOrderState as changeOrderStateAPI,
  getOrderStats
} from '../services/ordersService';
import { getProducts } from '@/modules/products/services/productsService';
import { getRoutings as getTechnologies } from '@/modules/routing/services/routingService';
import { getProductionLines, getCompanies } from '@/modules/basic-data/services/basicDataService';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/modules/auth/stores/authStore';
import { useRouter } from 'vue-router';

const router = useRouter();

// State
const orders = ref([]);
const products = ref([]);
const technologies = ref([]);
const productionLines = ref([]);
const companies = ref([]);
const loading = ref(false);
const saving = ref(false);
const changingState = ref(false);
const searchQuery = ref('');
const filterState = ref('');
const filterProductionLine = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const selectedRows = ref([]);

// Dialogs
const showCreateDialog = ref(false);
const showDetailsDialog = ref(false);
const showStateDialog = ref(false);
const showBulkStateDialog = ref(false);

// Forms and selected data
const editingOrder = ref(null);
const selectedOrder = ref(null);
const stateChangeOrder = ref(null);
const newState = ref('');
const bulkNewState = ref('');
const activeTab = ref('general');
const orderStateHistory = ref([]);
const orderFormRef = ref(null);

// Stats
const stats = ref({
  total: 0,
  pending: 0,
  in_progress: 0,
  completed: 0
});

const orderForm = ref({
  number: '',
  name: '',
  external_number: '',
  product: null,
  technology: null,
  production_line: null,
  company: null,
  planned_quantity: 1,
  done_quantity: 0,
  deadline: null,
  date_from: null,
  date_to: null,
  description: '',
});

const orderRules = {
  number: [
    { required: true, message: 'Please enter order number', trigger: 'blur' }
  ],
  name: [
    { required: true, message: 'Please enter order name', trigger: 'blur' }
  ],
  product: [
    { required: true, message: 'Please select a product', trigger: 'change' }
  ],
  planned_quantity: [
    { required: true, message: 'Please enter planned quantity', trigger: 'blur' },
    { validator: (rule, value, callback) => {
        if (value === null || value === undefined || value === '') return callback(new Error('Planned quantity required'));
        if (Number(value) <= 0) return callback(new Error('Planned quantity must be > 0'));
        callback();
      }, trigger: 'blur' }
  ]
};

// Auth
const auth = useAuthStore();
const { roles } = storeToRefs(auth);
const canManageOrders = computed(() => auth.hasRole(['Planner', 'Supervisor', 'Admin']));

// Methods
const loadStats = async () => {
  try {
    const data = await getOrderStats();
    stats.value = data;
  } catch (error) {
    console.error('Failed to load stats:', error);
  }
};

const loadOrders = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
    };
    if (filterState.value) params.state = filterState.value;
    if (filterProductionLine.value) params.production_line = filterProductionLine.value;
    
    const data = await getOrders(params);
    orders.value = data.results || data;
    total.value = data.count || orders.value.length;
    loadStats();
  } catch (error) {
    ElMessage.error('Failed to load orders');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const loadProducts = async () => {
  try {
    const data = await getProducts();
    products.value = data.results || data;
  } catch (error) {
    console.error('Failed to load products:', error);
  }
};

const loadTechnologies = async () => {
  try {
    const data = await getTechnologies();
    technologies.value = data.results || data;
  } catch (error) {
    console.error('Failed to load technologies:', error);
  }
};

const loadProductionLines = async () => {
  try {
    const data = await getProductionLines();
    productionLines.value = data.results || data;
  } catch (error) {
    console.error('Failed to load production lines:', error);
  }
};

const loadCompanies = async () => {
  try {
    const data = await getCompanies();
    companies.value = data.results || data;
  } catch (error) {
    console.error('Failed to load companies:', error);
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  loadOrders();
};

const handleSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1;
  loadOrders();
};

const handleSelectionChange = (selection) => {
  selectedRows.value = selection;
};

const handleProductChange = (productId) => {
  // Auto-select default technology for product if available
  const product = products.value.find(p => p.id === productId);
  if (product && product.default_technology) {
    orderForm.value.technology = product.default_technology;
  }
};

const viewOrderDetails = async (order) => {
  selectedOrder.value = order;
  orderStateHistory.value = order.state_changes || [];
  activeTab.value = 'general';
  showDetailsDialog.value = true;
};

const editOrder = (order) => {
  editingOrder.value = order;
  orderForm.value = {
    number: order.number,
    name: order.name,
    external_number: order.external_number || '',
    product: order.product,
    technology: order.technology,
    production_line: order.production_line,
    company: order.company,
    planned_quantity: parseFloat(order.planned_quantity),
    done_quantity: parseFloat(order.done_quantity),
    deadline: order.deadline ? new Date(order.deadline) : null,
    date_from: order.date_from ? new Date(order.date_from) : null,
    date_to: order.date_to ? new Date(order.date_to) : null,
    description: order.description || '',
  };
  showCreateDialog.value = true;
};

const resetForm = () => {
  orderForm.value = {
    number: '',
    name: '',
    external_number: '',
    product: null,
    technology: null,
    production_line: null,
    company: null,
    planned_quantity: 1,
    done_quantity: 0,
    deadline: null,
    date_from: null,
    date_to: null,
    description: '',
  };
  editingOrder.value = null;
};

const saveOrder = async () => {
  if (!orderFormRef.value) return;
  
  await orderFormRef.value.validate(async (valid) => {
    if (!valid) return;
    
    saving.value = true;
    try {
      const payload = {
        ...orderForm.value,
        deadline: orderForm.value.deadline?.toISOString() || null,
        date_from: orderForm.value.date_from?.toISOString() || null,
        date_to: orderForm.value.date_to?.toISOString() || null,
        external_number: orderForm.value.external_number ? orderForm.value.external_number : null,
      };
      
      if (editingOrder.value) {
        await updateOrder(editingOrder.value.id, payload);
        ElMessage.success('Order updated successfully');
      } else {
        await createOrder(payload);
        ElMessage.success('Order created successfully');
      }
      
      showCreateDialog.value = false;
      resetForm();
      loadOrders();
    } catch (error) {
      // Try to surface first field error if present
      const data = error.response?.data;
      let msg = data?.error;
      if (!msg && data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0];
        if (firstKey && Array.isArray(data[firstKey]) && data[firstKey].length) {
          msg = `${firstKey}: ${data[firstKey][0]}`;
        }
      }
      ElMessage.error(msg || 'Failed to save order');
      console.error('Order save error payload:', data);
    } finally {
      saving.value = false;
    }
  });
};

const handleOrderAction = (command, order) => {
  switch (command) {
    case 'edit':
      editOrder(order);
      break;
    case 'state':
      stateChangeOrder.value = order;
      newState.value = order.state;
      showStateDialog.value = true;
      break;
    case 'schedule':
      router.push('/scheduling');
      break;
    case 'copy':
      copyOrder(order);
      break;
    case 'delete':
      confirmDeleteOrder(order);
      break;
  }
};

const copyOrder = (order) => {
  orderForm.value = {
    number: '',
    name: order.name + ' (Copy)',
    external_number: '',
    product: order.product,
    technology: order.technology,
    production_line: order.production_line,
    company: order.company,
    planned_quantity: parseFloat(order.planned_quantity),
    done_quantity: 0,
    deadline: order.deadline ? new Date(order.deadline) : null,
    date_from: null,
    date_to: null,
    description: order.description || '',
  };
  editingOrder.value = null;
  showCreateDialog.value = true;
};

const confirmDeleteOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete order "${order.number}"? This action cannot be undone.`,
      'Delete Order',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
    
    await deleteOrder(order.id);
    ElMessage.success('Order deleted successfully');
    loadOrders();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete order');
      console.error(error);
    }
  }
};

const changeOrderState = async () => {
  if (!newState.value) {
    ElMessage.warning('Please select a new state');
    return;
  }
  
  changingState.value = true;
  try {
    await changeOrderStateAPI(stateChangeOrder.value.id, {
      state: newState.value,
      worker: auth.user?.username || ''
    });
    
    ElMessage.success('Order state changed successfully');
    showStateDialog.value = false;
    loadOrders();
  } catch (error) {
    ElMessage.error('Failed to change order state');
    console.error(error);
  } finally {
    changingState.value = false;
  }
};

const bulkChangeState = async () => {
  if (!bulkNewState.value) {
    ElMessage.warning('Please select a new state');
    return;
  }
  
  changingState.value = true;
  try {
    const promises = selectedRows.value.map(order => 
      changeOrderStateAPI(order.id, {
        state: bulkNewState.value,
        worker: auth.user?.username || ''
      })
    );
    
    await Promise.all(promises);
    ElMessage.success(`${selectedRows.value.length} orders updated successfully`);
    showBulkStateDialog.value = false;
    bulkNewState.value = '';
    loadOrders();
  } catch (error) {
    ElMessage.error('Failed to change order states');
    console.error(error);
  } finally {
    changingState.value = false;
  }
};

// Utility functions
const getStateType = (state) => {
  const types = {
    pending: 'warning',
    accepted: 'info',
    in_progress: '',
    completed: 'success',
    declined: 'danger',
    interrupted: 'warning',
    abandoned: 'info'
  };
  return types[state] || '';
};

const formatState = (state) => {
  return state.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getDeadlineClass = (deadline) => {
  const now = new Date();
  const deadlineDate = new Date(deadline);
  const daysUntil = (deadlineDate - now) / (1000 * 60 * 60 * 24);
  
  if (daysUntil < 0) return 'deadline overdue';
  if (daysUntil < 2) return 'deadline urgent';
  if (daysUntil < 7) return 'deadline warning';
  return 'deadline normal';
};

const getProgressPercentage = (order) => {
  const planned = parseFloat(order.planned_quantity);
  const done = parseFloat(order.done_quantity);
  if (planned === 0) return 0;
  return Math.min(Math.round((done / planned) * 100), 100);
};

const getProgressStatus = (order) => {
  const percentage = getProgressPercentage(order);
  if (percentage === 100) return 'success';
  if (percentage >= 75) return '';
  if (percentage >= 50) return 'warning';
  return 'exception';
};

// Lifecycle
onMounted(() => {
  loadOrders();
  loadProducts();
  loadTechnologies();
  loadProductionLines();
  loadCompanies();
});
</script>

<style scoped>
.orders-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 16px 0;
  font-size: 24px;
  color: #303133;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.pending :deep(.el-statistic__content) {
  color: #e6a23c;
}

.stat-card.in-progress :deep(.el-statistic__content) {
  color: #409eff;
}

.stat-card.completed :deep(.el-statistic__content) {
  color: #67c23a;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.product-name {
  font-weight: 500;
  color: #303133;
}

.product-number {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.quantity-info {
  text-align: center;
}

.quantity-info > div:first-child {
  margin-bottom: 4px;
  font-weight: 500;
}

.deadline {
  display: flex;
  align-items: center;
  gap: 4px;
}

.deadline.normal {
  color: #606266;
}

.deadline.warning {
  color: #e6a23c;
}

.deadline.urgent {
  color: #f56c6c;
  font-weight: 500;
}

.deadline.overdue {
  color: #f56c6c;
  font-weight: 600;
  text-decoration: line-through;
}

.text-muted {
  color: #909399;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  display: block;
  margin-top: 4px;
}

.order-details {
  min-height: 300px;
}

.worker-info {
  font-size: 13px;
  color: #606266;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

:deep(.el-pagination) {
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table .cell) {
  display: flex;
  align-items: center;
}

:deep(.el-progress) {
  margin-top: 4px;
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-left, .toolbar-right {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
