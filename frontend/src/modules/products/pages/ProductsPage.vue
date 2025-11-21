<template>
  <div class="products-page">
    <!-- Header with Stats -->
    <div class="page-header">
      <h1>Products Management</h1>
      <div class="stats-cards">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="Total Products" :value="stats.total" />
        </el-card>
        <el-card shadow="hover" class="stat-card component">
          <el-statistic title="Components" :value="stats.components" />
        </el-card>
        <el-card shadow="hover" class="stat-card intermediate">
          <el-statistic title="Intermediate" :value="stats.intermediate" />
        </el-card>
        <el-card shadow="hover" class="stat-card final">
          <el-statistic title="Final Products" :value="stats.final_products" />
        </el-card>
      </div>
    </div>

    <el-card>
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button
            v-if="canManageProducts"
            type="primary"
            :icon="Plus"
            @click="openCreateDialog"
          >
            Create Product
          </el-button>
          <el-button :icon="Refresh" @click="loadProducts"> Refresh </el-button>
          <el-button
            v-if="canManageProducts && selectedRows.length > 0"
            :icon="Delete"
            @click="bulkDelete"
          >
            Delete ({{ selectedRows.length }})
          </el-button>
          <el-dropdown
            v-if="canManageProducts"
            trigger="click"
            @command="handleBulkAction"
          >
            <el-button :icon="MoreFilled"> Bulk Actions </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="activate" :icon="Select"
                  >Activate Selected</el-dropdown-item
                >
                <el-dropdown-item command="deactivate" :icon="Close"
                  >Deactivate Selected</el-dropdown-item
                >
                <el-dropdown-item command="export" :icon="Download"
                  >Export to CSV</el-dropdown-item
                >
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <div class="toolbar-right">
          <el-input
            v-model="searchQuery"
            placeholder="Search by number, name, EAN..."
            style="width: 280px"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-select
            v-model="filterType"
            placeholder="Type"
            clearable
            @change="loadProducts"
            style="margin-left: 10px; width: 160px"
          >
            <el-option label="All Types" value="" />
            <el-option label="Component" value="component" />
            <el-option label="Intermediate" value="intermediate" />
            <el-option label="Final Product" value="final_product" />
            <el-option label="Waste" value="waste" />
            <el-option label="Package" value="package" />
          </el-select>

          <el-select
            v-model="filterActive"
            placeholder="Status"
            clearable
            @change="loadProducts"
            style="margin-left: 10px; width: 130px"
          >
            <el-option label="All Status" value="" />
            <el-option label="Active" value="true" />
            <el-option label="Inactive" value="false" />
          </el-select>
        </div>
      </div>

      <!-- Products Table -->
      <el-table
        :data="products"
        style="width: 100%; margin-top: 20px"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        row-key="id"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column
          prop="number"
          label="Product Number"
          width="140"
          sortable
        >
          <template #default="scope">
            <el-link type="primary" @click="viewProductDetails(scope.row)">
              {{ scope.row.number }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column
          prop="name"
          label="Name"
          min-width="200"
          show-overflow-tooltip
        />
        <el-table-column
          prop="global_type_of_material"
          label="Type"
          width="130"
        >
          <template #default="scope">
            <el-tag
              :type="getTypeColor(scope.row.global_type_of_material)"
              size="small"
            >
              {{ formatType(scope.row.global_type_of_material) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Unit" width="100" align="center">
          <template #default="scope">
            <div>
              <el-tag size="small">{{ scope.row.unit }}</el-tag>
              <div v-if="scope.row.additional_unit" class="additional-unit">
                + {{ scope.row.additional_unit }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="ean"
          label="EAN"
          width="140"
          show-overflow-tooltip
        />
        <el-table-column
          label="Supplier/Producer"
          width="150"
          show-overflow-tooltip
        >
          <template #default="scope">
            <div v-if="scope.row.supplier_name || scope.row.producer_name">
              <div v-if="scope.row.supplier_name" class="company-info">
                <el-icon><ShoppingCart /></el-icon>
                {{ scope.row.supplier_name }}
              </div>
              <div v-if="scope.row.producer_name" class="company-info">
                <el-icon><Operation /></el-icon>
                {{ scope.row.producer_name }}
              </div>
            </div>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100" align="center">
          <template #default="scope">
            <el-switch
              v-model="scope.row.active"
              :disabled="!canManageProducts"
              @change="toggleActive(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button
                size="small"
                :icon="View"
                @click="viewProductDetails(scope.row)"
              >
                View
              </el-button>
              <el-dropdown
                v-if="canManageProducts"
                trigger="click"
                @command="handleProductAction($event, scope.row)"
              >
                <el-button size="small" :icon="More" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit" :icon="Edit"
                      >Edit</el-dropdown-item
                    >
                    <el-dropdown-item command="copy" :icon="CopyDocument"
                      >Duplicate</el-dropdown-item
                    >
                    <el-dropdown-item command="routing" :icon="List"
                      >View Routing</el-dropdown-item
                    >
                    <el-dropdown-item divided command="delete" :icon="Delete"
                      >Delete</el-dropdown-item
                    >
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
        @current-change="loadProducts"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- Create/Edit Product Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProduct ? 'Edit Product' : 'Create New Product'"
      width="750px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="productForm"
        :rules="productRules"
        ref="productFormRef"
        label-width="160px"
      >
        <el-tabs v-model="activeFormTab">
          <el-tab-pane label="Basic Information" name="basic">
            <el-form-item label="Product Number" prop="number">
              <el-input v-model="productForm.number" placeholder="AUTO" />
              <span class="form-hint">Leave empty for auto-generation</span>
            </el-form-item>

            <el-form-item label="Product Name" prop="name">
              <el-input v-model="productForm.name" />
            </el-form-item>

            <el-form-item label="External Number">
              <el-input
                v-model="productForm.external_number"
                placeholder="External reference"
              />
            </el-form-item>

            <el-form-item label="Type" prop="global_type_of_material">
              <el-select
                v-model="productForm.global_type_of_material"
                style="width: 100%"
              >
                <el-option label="Component" value="component" />
                <el-option label="Intermediate" value="intermediate" />
                <el-option label="Final Product" value="final_product" />
                <el-option label="Waste" value="waste" />
                <el-option label="Package" value="package" />
              </el-select>
            </el-form-item>

            <el-form-item label="Entity Type">
              <el-select v-model="productForm.entity_type" style="width: 100%">
                <el-option
                  label="Particular Product"
                  value="particular_product"
                />
                <el-option label="Products Family" value="products_family" />
              </el-select>
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Unit" prop="unit">
                  <el-input
                    v-model="productForm.unit"
                    placeholder="e.g., pcs, kg, m"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Additional Unit">
                  <el-input
                    v-model="productForm.additional_unit"
                    placeholder="e.g., box, pallet"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item
              label="Conversion Factor"
              v-if="productForm.additional_unit"
            >
              <el-input-number
                v-model="productForm.conversion"
                :min="0.00001"
                :precision="5"
                style="width: 100%"
              />
              <span class="form-hint"
                >1 {{ productForm.additional_unit }} = X
                {{ productForm.unit }}</span
              >
            </el-form-item>

            <el-form-item label="EAN / Barcode">
              <el-input
                v-model="productForm.ean"
                placeholder="EAN-13 or barcode"
              />
            </el-form-item>

            <el-form-item label="Description">
              <el-input
                v-model="productForm.description"
                type="textarea"
                :rows="4"
                placeholder="Product description, notes, specifications..."
              />
            </el-form-item>

            <el-form-item label="Active">
              <el-switch v-model="productForm.active" />
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="Relationships" name="relations">
            <el-form-item label="Parent Product">
              <el-select
                v-model="productForm.parent"
                filterable
                clearable
                placeholder="Select parent product family"
                style="width: 100%"
              >
                <el-option
                  v-for="product in familyProducts"
                  :key="product.id"
                  :label="`${product.number} - ${product.name}`"
                  :value="product.id"
                />
              </el-select>
              <span class="form-hint">For product variants/families</span>
            </el-form-item>

            <el-form-item label="Supplier">
              <el-select
                v-model="productForm.supplier"
                filterable
                clearable
                placeholder="Select supplier company"
                style="width: 100%"
              >
                <el-option
                  v-for="company in companies"
                  :key="company.id"
                  :label="`${company.number} - ${company.name}`"
                  :value="company.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Producer">
              <el-select
                v-model="productForm.producer"
                filterable
                clearable
                placeholder="Select producer company"
                style="width: 100%"
              >
                <el-option
                  v-for="company in companies"
                  :key="company.id"
                  :label="`${company.number} - ${company.name}`"
                  :value="company.id"
                />
              </el-select>
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="Work Masters (Recipes)" name="recipes">
            <el-alert
              title="Define the 'How-To' of production here"
              type="info"
              show-icon
              :closable="false"
              class="mb-4"
            />

            <el-form-item label="Default Recipe">
              <el-input
                v-model="productForm.default_recipe"
                placeholder="e.g., Standard Assembly v1.0"
              />
            </el-form-item>

            <el-form-item label="Workflow Steps">
              <el-input
                v-model="productForm.workflow_steps"
                type="textarea"
                :rows="6"
                placeholder="1. Prepare material...&#10;2. Assemble part A...&#10;3. Inspect..."
              />
            </el-form-item>

            <el-form-item label="Version Control">
              <el-input
                v-model="productForm.version"
                placeholder="v1.0"
                style="width: 120px"
              />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveProduct" :loading="saving">
          {{ editingProduct ? "Update" : "Create" }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Product Details Dialog -->
    <el-dialog
      v-model="showDetailsDialog"
      :title="'Product Details: ' + (selectedProduct?.number || '')"
      width="900px"
    >
      <div v-if="selectedProduct" class="product-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Product Number">
            {{ selectedProduct.number }}
          </el-descriptions-item>
          <el-descriptions-item label="Product Name">
            {{ selectedProduct.name }}
          </el-descriptions-item>
          <el-descriptions-item label="External Number">
            {{ selectedProduct.external_number || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="Type">
            <el-tag
              :type="getTypeColor(selectedProduct.global_type_of_material)"
            >
              {{ formatType(selectedProduct.global_type_of_material) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Entity Type">
            {{ formatEntityType(selectedProduct.entity_type) }}
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedProduct.active ? 'success' : 'info'">
              {{ selectedProduct.active ? "Active" : "Inactive" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Unit">
            {{ selectedProduct.unit }}
          </el-descriptions-item>
          <el-descriptions-item label="Additional Unit">
            {{ selectedProduct.additional_unit || "-" }}
          </el-descriptions-item>
          <el-descriptions-item
            label="Conversion"
            v-if="selectedProduct.conversion"
          >
            1 {{ selectedProduct.additional_unit }} =
            {{ selectedProduct.conversion }} {{ selectedProduct.unit }}
          </el-descriptions-item>
          <el-descriptions-item label="EAN / Barcode">
            {{ selectedProduct.ean || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="Parent Product">
            {{ selectedProduct.parent_name || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="Supplier">
            {{ selectedProduct.supplier_name || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="Producer">
            {{ selectedProduct.producer_name || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="Created">
            {{ formatDateTime(selectedProduct.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="Last Updated">
            {{ formatDateTime(selectedProduct.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">
            {{ selectedProduct.description || "-" }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  Refresh,
  Search,
  View,
  Edit,
  Delete,
  More,
  MoreFilled,
  CopyDocument,
  List,
  ShoppingCart,
  Operation,
  Select,
  Close,
  Download,
} from "@element-plus/icons-vue";
import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from "../services/productsService";
import { getCompanies } from "@/modules/basic-data/services/basicDataService";
import { storeToRefs } from "pinia";
import { useAuthStore } from "@/modules/auth/stores/authStore";
import { useRouter } from "vue-router";

const router = useRouter();

// State
const products = ref([]);
const companies = ref([]);
const familyProducts = ref([]);
const loading = ref(false);
const saving = ref(false);
const searchQuery = ref("");
const filterType = ref("");
const filterActive = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const selectedRows = ref([]);

// Dialogs
const showCreateDialog = ref(false);
const showDetailsDialog = ref(false);

// Forms
const editingProduct = ref(null);
const selectedProduct = ref(null);
const activeFormTab = ref("basic");
const productFormRef = ref(null);

// Stats
const stats = ref({
  total: 0,
  components: 0,
  intermediate: 0,
  final_products: 0,
});

const productForm = ref({
  number: "",
  name: "",
  external_number: "",
  global_type_of_material: "component",
  entity_type: "particular_product",
  unit: "pcs",
  additional_unit: "",
  conversion: null,
  ean: "",
  description: "",
  parent: null,
  supplier: null,
  producer: null,
  active: true,
});

const productRules = {
  name: [
    { required: true, message: "Please enter product name", trigger: "blur" },
  ],
  unit: [{ required: true, message: "Please enter unit", trigger: "blur" }],
  global_type_of_material: [
    { required: true, message: "Please select type", trigger: "change" },
  ],
};

// Auth
const auth = useAuthStore();
const canManageProducts = computed(() =>
  auth.hasRole(["Planner", "Supervisor", "Admin"])
);

// Methods
const calculateStats = () => {
  stats.value.total = products.value.length;
  stats.value.components = products.value.filter(
    (p) => p.global_type_of_material === "component"
  ).length;
  stats.value.intermediate = products.value.filter(
    (p) => p.global_type_of_material === "intermediate"
  ).length;
  stats.value.final_products = products.value.filter(
    (p) => p.global_type_of_material === "final_product"
  ).length;
};

const loadProducts = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
    };
    if (filterType.value) params.global_type_of_material = filterType.value;
    if (filterActive.value !== "") params.active = filterActive.value;

    const data = await getProducts(params);
    products.value = data.results || data;
    total.value = data.count || products.value.length;
    calculateStats();
  } catch (error) {
    ElMessage.error("Failed to load products");
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const loadCompanies = async () => {
  try {
    const data = await getCompanies();
    companies.value = data.results || data;
  } catch (error) {
    console.error("Failed to load companies:", error);
  }
};

const loadFamilyProducts = async () => {
  try {
    const data = await getProducts({ entity_type: "products_family" });
    familyProducts.value = data.results || data;
  } catch (error) {
    console.error("Failed to load family products:", error);
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  loadProducts();
};

const handleSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1;
  loadProducts();
};

const handleSelectionChange = (selection) => {
  selectedRows.value = selection;
};

const openCreateDialog = () => {
  resetForm();
  showCreateDialog.value = true;
};

const viewProductDetails = (product) => {
  selectedProduct.value = product;
  showDetailsDialog.value = true;
};

const editProduct = (product) => {
  editingProduct.value = product;
  productForm.value = {
    number: product.number,
    name: product.name,
    external_number: product.external_number || "",
    global_type_of_material: product.global_type_of_material,
    entity_type: product.entity_type || "particular_product",
    unit: product.unit,
    additional_unit: product.additional_unit || "",
    conversion: product.conversion ? parseFloat(product.conversion) : null,
    ean: product.ean || "",
    description: product.description || "",
    parent: product.parent,
    supplier: product.supplier,
    producer: product.producer,
    active: product.active,
  };
  activeFormTab.value = "basic";
  showCreateDialog.value = true;
};

const resetForm = () => {
  productForm.value = {
    number: "",
    name: "",
    external_number: "",
    global_type_of_material: "component",
    entity_type: "particular_product",
    unit: "pcs",
    additional_unit: "",
    conversion: null,
    ean: "",
    description: "",
    parent: null,
    supplier: null,
    producer: null,
    active: true,
  };
  editingProduct.value = null;
};

const saveProduct = async () => {
  if (!productFormRef.value) return;

  await productFormRef.value.validate(async (valid) => {
    if (!valid) return;

    saving.value = true;
    try {
      const payload = { ...productForm.value };

      if (editingProduct.value) {
        await updateProduct(editingProduct.value.id, payload);
        ElMessage.success("Product updated successfully");
      } else {
        await createProduct(payload);
        ElMessage.success("Product created successfully");
      }

      showCreateDialog.value = false;
      resetForm();
      loadProducts();
    } catch (error) {
      ElMessage.error(error.response?.data?.error || "Failed to save product");
      console.error(error);
    } finally {
      saving.value = false;
    }
  });
};

const handleProductAction = (command, product) => {
  switch (command) {
    case "edit":
      editProduct(product);
      break;
    case "copy":
      duplicateProduct(product);
      break;
    case "routing":
      router.push(`/routing?product=${product.id}`);
      break;
    case "delete":
      confirmDeleteProduct(product);
      break;
  }
};

const duplicateProduct = (product) => {
  productForm.value = {
    number: "",
    name: product.name + " (Copy)",
    external_number: "",
    global_type_of_material: product.global_type_of_material,
    entity_type: product.entity_type || "particular_product",
    unit: product.unit,
    additional_unit: product.additional_unit || "",
    conversion: product.conversion ? parseFloat(product.conversion) : null,
    ean: "",
    description: product.description || "",
    parent: product.parent,
    supplier: product.supplier,
    producer: product.producer,
    active: true,
  };
  editingProduct.value = null;
  activeFormTab.value = "basic";
  showCreateDialog.value = true;
};

const confirmDeleteProduct = async (product) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete product "${product.number}"? This action cannot be undone.`,
      "Delete Product",
      {
        confirmButtonText: "Delete",
        cancelButtonText: "Cancel",
        type: "warning",
        confirmButtonClass: "el-button--danger",
      }
    );

    await deleteProduct(product.id);
    ElMessage.success("Product deleted successfully");
    loadProducts();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("Failed to delete product");
      console.error(error);
    }
  }
};

const toggleActive = async (product) => {
  try {
    await updateProduct(product.id, { active: product.active });
    ElMessage.success(
      `Product ${product.active ? "activated" : "deactivated"}`
    );
  } catch (error) {
    product.active = !product.active; // Revert on error
    ElMessage.error("Failed to update product status");
    console.error(error);
  }
};

const handleBulkAction = async (command) => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning("Please select products first");
    return;
  }

  switch (command) {
    case "activate":
    case "deactivate":
      await bulkToggleActive(command === "activate");
      break;
    case "export":
      exportToCSV();
      break;
  }
};

const bulkToggleActive = async (active) => {
  try {
    const promises = selectedRows.value.map((product) =>
      updateProduct(product.id, { active })
    );
    await Promise.all(promises);
    ElMessage.success(`${selectedRows.value.length} products updated`);
    loadProducts();
  } catch (error) {
    ElMessage.error("Failed to update products");
    console.error(error);
  }
};

const bulkDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete ${selectedRows.value.length} selected products? This action cannot be undone.`,
      "Bulk Delete",
      {
        confirmButtonText: "Delete",
        cancelButtonText: "Cancel",
        type: "warning",
        confirmButtonClass: "el-button--danger",
      }
    );

    const promises = selectedRows.value.map((product) =>
      deleteProduct(product.id)
    );
    await Promise.all(promises);
    ElMessage.success(`${selectedRows.value.length} products deleted`);
    loadProducts();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("Failed to delete products");
      console.error(error);
    }
  }
};

const exportToCSV = () => {
  const headers = ["Number", "Name", "Type", "Unit", "EAN", "Status"];
  const data = selectedRows.value.map((p) => [
    p.number,
    p.name,
    p.global_type_of_material,
    p.unit,
    p.ean || "",
    p.active ? "Active" : "Inactive",
  ]);

  const csv = [
    headers.join(","),
    ...data.map((row) => row.map((cell) => `"${cell}"`).join(",")),
  ].join("\n");

  const blob = new Blob([csv], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `products_${new Date().toISOString().split("T")[0]}.csv`;
  a.click();
  window.URL.revokeObjectURL(url);

  ElMessage.success("Products exported to CSV");
};

// Utility functions
const getTypeColor = (type) => {
  const colors = {
    component: "",
    intermediate: "warning",
    final_product: "success",
    waste: "danger",
    package: "info",
  };
  return colors[type] || "";
};

const formatType = (type) => {
  return type
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const formatEntityType = (type) => {
  return type
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const formatDateTime = (dateStr) => {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// Lifecycle
onMounted(() => {
  loadProducts();
  loadCompanies();
  loadFamilyProducts();
});
</script>

<style scoped>
.products-page {
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

.stat-card.component :deep(.el-statistic__content) {
  color: #409eff;
}

.stat-card.intermediate :deep(.el-statistic__content) {
  color: #e6a23c;
}

.stat-card.final :deep(.el-statistic__content) {
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

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.additional-unit {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.company-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
  margin: 2px 0;
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

.product-details {
  min-height: 300px;
}

:deep(.el-pagination) {
  display: flex;
  justify-content: flex-end;
}

:deep(.el-tabs__content) {
  padding-top: 20px;
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
