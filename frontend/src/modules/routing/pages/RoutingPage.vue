<template>
  <div class="routing">
    <h1>Routing Management</h1>
    
    <!-- Stats Dashboard -->
    <div class="stats-container">
      <el-card class="stat-card stat-total">
        <div class="stat-content">
          <div class="stat-icon">📋</div>
          <div class="stat-info">
            <div class="stat-label">Total Routings</div>
            <div class="stat-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-draft">
        <div class="stat-content">
          <div class="stat-icon">✏️</div>
          <div class="stat-info">
            <div class="stat-label">Draft</div>
            <div class="stat-value">{{ stats.by_state?.draft || 0 }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-accepted">
        <div class="stat-content">
          <div class="stat-icon">✓</div>
          <div class="stat-info">
            <div class="stat-label">Accepted</div>
            <div class="stat-value">{{ stats.by_state?.accepted || 0 }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-master">
        <div class="stat-content">
          <div class="stat-icon">⭐</div>
          <div class="stat-info">
            <div class="stat-label">Master Routings</div>
            <div class="stat-value">{{ stats.master || 0 }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <el-card>
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button v-if="canEditTech" type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> Create Routing
          </el-button>
          
          <el-dropdown v-if="canEditTech && selectedTechnologies.length > 0" @command="handleBulkAction" style="margin-left: 10px;">
            <el-button>
              Bulk Actions ({{ selectedTechnologies.length }}) <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="accept">Accept</el-dropdown-item>
                <el-dropdown-item command="check">Check</el-dropdown-item>
                <el-dropdown-item command="decline">Decline</el-dropdown-item>
                <el-dropdown-item divided command="activate">Activate</el-dropdown-item>
                <el-dropdown-item command="deactivate">Deactivate</el-dropdown-item>
                <el-dropdown-item divided command="delete" style="color: #f56c6c;">Delete</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <el-button @click="exportToCSV" style="margin-left: 10px;">
            <el-icon><Download /></el-icon> Export CSV
          </el-button>
        </div>
        
        <div class="toolbar-right">
          <el-input
            v-model="searchQuery"
            placeholder="Search routings..."
            style="width: 250px;"
            @input="handleSearch"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-model="filterState" placeholder="State" @change="loadTechnologies" style="margin-left: 10px; width: 130px;" clearable>
            <el-option label="All States" value="" />
            <el-option label="Draft" value="draft" />
            <el-option label="Accepted" value="accepted" />
            <el-option label="Checked" value="checked" />
            <el-option label="Outdated" value="outdated" />
            <el-option label="Declined" value="declined" />
          </el-select>
          
          <el-select v-model="filterMaster" placeholder="Master" @change="loadTechnologies" style="margin-left: 10px; width: 120px;" clearable>
            <el-option label="All" value="" />
            <el-option label="Master" value="true" />
            <el-option label="Non-Master" value="false" />
          </el-select>
          
          <el-select v-model="filterActive" placeholder="Status" @change="loadTechnologies" style="margin-left: 10px; width: 120px;" clearable>
            <el-option label="All" value="" />
            <el-option label="Active" value="true" />
            <el-option label="Inactive" value="false" />
          </el-select>
        </div>
      </div>

      <!-- Routing Table -->
      <el-table 
        :data="technologies" 
        style="width: 100%; margin-top: 20px;" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="number" label="Number" width="140" sortable />
        <el-table-column prop="name" label="Name" min-width="200" />
        <el-table-column prop="product_name" label="Product" min-width="150" />
        <el-table-column prop="state" label="State" width="110">
          <template #default="scope">
            <el-tag :type="getStateType(scope.row.state)" size="small">{{ scope.row.state }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Master" width="80" align="center">
          <template #default="scope">
            <el-icon v-if="scope.row.master" color="#f59e0b" :size="18"><StarFilled /></el-icon>
          </template>
        </el-table-column>
        <el-table-column label="Active" width="80" align="center">
          <template #default="scope">
            <el-switch 
              v-model="scope.row.active" 
              @change="toggleActive(scope.row)"
              :disabled="!canEditTech"
            />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="280" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewTechnology(scope.row)">
              <el-icon><View /></el-icon> View
            </el-button>
            <el-button v-if="canEditTech" size="small" type="primary" @click="editTechnology(scope.row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-dropdown v-if="canEditTech" @command="(cmd) => handleActionMenu(scope.row, cmd)" style="margin-left: 5px;">
              <el-button size="small">
                More <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="tree">
                    <el-icon><Share /></el-icon> View Tree
                  </el-dropdown-item>
                  <el-dropdown-item command="accept">
                    <el-icon><Check /></el-icon> Accept
                  </el-dropdown-item>
                  <el-dropdown-item command="check">
                    <el-icon><CircleCheck /></el-icon> Check
                  </el-dropdown-item>
                  <el-dropdown-item command="setMaster" :disabled="scope.row.master">
                    <el-icon><StarFilled /></el-icon> Set as Master
                  </el-dropdown-item>
                  <el-dropdown-item divided command="copy">
                    <el-icon><DocumentCopy /></el-icon> Copy
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" style="color: #f56c6c;">
                    <el-icon><Delete /></el-icon> Delete
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next, jumper"
        @current-change="loadTechnologies"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingTechnology ? 'Edit Routing' : 'Create Routing'" 
      width="700px"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="activeTab">
        <el-tab-pane label="Basic Information" name="basic">
          <el-form :model="technologyForm" label-width="140px" style="padding: 10px 20px;">
            <el-form-item label="Number" required>
              <el-input v-model="technologyForm.number" placeholder="e.g., TECH-001" />
            </el-form-item>
            <el-form-item label="Name" required>
              <el-input v-model="technologyForm.name" placeholder="Routing name" />
            </el-form-item>
            <el-form-item label="Product" required>
              <el-select v-model="technologyForm.product" filterable placeholder="Select Product" style="width: 100%;">
                <el-option v-for="product in products" :key="product.id" :label="`${product.number} - ${product.name}`" :value="product.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="Description">
              <el-input v-model="technologyForm.description" type="textarea" :rows="4" placeholder="Describe the routing..." />
            </el-form-item>
            <el-form-item label="State">
              <el-select v-model="technologyForm.state" style="width: 100%;">
                <el-option label="Draft" value="draft" />
                <el-option label="Accepted" value="accepted" />
                <el-option label="Checked" value="checked" />
                <el-option label="Outdated" value="outdated" />
                <el-option label="Declined" value="declined" />
              </el-select>
            </el-form-item>
            <el-form-item label="Master Routing">
              <el-switch v-model="technologyForm.master" />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                Set as the main routing for this product
              </span>
            </el-form-item>
            <el-form-item label="Active">
              <el-switch v-model="technologyForm.active" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="Operations" name="operations" :disabled="!editingTechnology">
          <div v-if="editingTechnology" style="padding: 10px 20px;">
            <!-- Operations List -->
            <div style="margin-bottom: 15px;">
              <el-button type="primary" size="small" @click="showAddOperationDialog = true">
                <el-icon><Plus /></el-icon> Add Operation
              </el-button>
              <el-button size="small" @click="loadOperationComponents" style="margin-left: 10px;">
                <el-icon><Refresh /></el-icon> Refresh
              </el-button>
            </div>

            <el-table 
              :data="operationComponents" 
              style="width: 100%;" 
              v-loading="loadingOperations"
              :empty-text="'No operations added yet'"
            >
              <el-table-column prop="node_number" label="Node" width="100" />
              <el-table-column prop="operation_name" label="Operation" min-width="150" />
              <el-table-column prop="priority" label="Priority" width="80" align="center" />
              <el-table-column label="Times" width="180">
                <template #default="scope">
                  <div style="font-size: 12px; color: #606266;">
                    <div>TJ: {{ scope.row.tj || scope.row.operation?.tj || 0 }}s</div>
                    <div>TPZ: {{ scope.row.tpz || scope.row.operation?.tpz || 0 }}s</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Products" min-width="200">
                <template #default="scope">
                  <div style="font-size: 11px;">
                    <div v-if="scope.row.input_products?.length" style="margin-bottom: 3px;">
                      <el-tag type="warning" size="small" effect="plain">In:</el-tag>
                      <span style="margin-left: 5px;">{{ scope.row.input_products.length }} items</span>
                    </div>
                    <div v-if="scope.row.output_products?.length">
                      <el-tag type="success" size="small" effect="plain">Out:</el-tag>
                      <span style="margin-left: 5px;">{{ scope.row.output_products.length }} items</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Actions" width="180" fixed="right">
                <template #default="scope">
                  <el-button size="small" @click="editOperationComponent(scope.row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button size="small" @click="manageProducts(scope.row)">
                    <el-icon><Box /></el-icon> Products
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click="deleteOperationComponent(scope.row)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div v-else style="padding: 20px; text-align: center; color: #909399;">
            Save the routing first to add operations
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <template #footer>
        <el-button @click="closeDialog">Cancel</el-button>
        <el-button type="primary" @click="saveTechnology" :loading="saving">
          {{ editingTechnology ? 'Update' : 'Create' }} Routing
        </el-button>
      </template>
    </el-dialog>

    <!-- Routing Details Dialog -->
    <el-dialog v-model="showDetailsDialog" title="Routing Details" width="800px">
      <el-descriptions v-if="selectedTech" :column="2" border>
        <el-descriptions-item label="Number">{{ selectedTech.number }}</el-descriptions-item>
        <el-descriptions-item label="Name">{{ selectedTech.name }}</el-descriptions-item>
        <el-descriptions-item label="Product">{{ selectedTech.product_name }}</el-descriptions-item>
        <el-descriptions-item label="State">
          <el-tag :type="getStateType(selectedTech.state)">{{ selectedTech.state }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Master">
          <el-tag v-if="selectedTech.master" type="warning">Master</el-tag>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Active">
          <el-tag :type="selectedTech.active ? 'success' : 'info'">
            {{ selectedTech.active ? 'Active' : 'Inactive' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">
          {{ selectedTech.description || 'No description' }}
        </el-descriptions-item>
        <el-descriptions-item label="Created">{{ formatDate(selectedTech.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="Updated">{{ formatDate(selectedTech.updated_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Operation Tree Dialog -->
    <el-dialog v-model="showTreeDialog" title="Routing Operation Tree" width="900px" top="5vh">
      <div v-if="technologyTree" style="max-height: 70vh; overflow-y: auto;">
        <!-- Summary -->
        <el-card style="margin-bottom: 15px;" shadow="never">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <h3 style="margin: 0 0 5px 0;">{{ technologyTree.technology?.name }}</h3>
              <div style="color: #909399; font-size: 13px;">
                Product: {{ technologyTree.technology?.product }} | State: {{ technologyTree.technology?.state }}
              </div>
            </div>
            <div style="text-align: right;">
              <div style="font-size: 12px; color: #909399;">Total Operations</div>
              <div style="font-size: 24px; font-weight: bold; color: #409eff;">{{ technologyTree.summary?.nodes || 0 }}</div>
            </div>
          </div>
        </el-card>

        <!-- Time Summary -->
        <el-row :gutter="10" style="margin-bottom: 15px;">
          <el-col :span="8">
            <el-card shadow="hover" body-style="padding: 15px;">
              <div style="text-align: center;">
                <div style="font-size: 12px; color: #909399; margin-bottom: 5px;">Total Batch Time (TJ)</div>
                <div style="font-size: 20px; font-weight: bold; color: #67c23a;">
                  {{ formatTime(technologyTree.summary?.total_tj || 0) }}
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" body-style="padding: 15px;">
              <div style="text-align: center;">
                <div style="font-size: 12px; color: #909399; margin-bottom: 5px;">Total Prep Time (TPZ)</div>
                <div style="font-size: 20px; font-weight: bold; color: #e6a23c;">
                  {{ formatTime(technologyTree.summary?.total_tpz || 0) }}
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" body-style="padding: 15px;">
              <div style="text-align: center;">
                <div style="font-size: 12px; color: #909399; margin-bottom: 5px;">Next Operation Time</div>
                <div style="font-size: 20px; font-weight: bold; color: #409eff;">
                  {{ formatTime(technologyTree.summary?.total_time_next_operation || 0) }}
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- Operation Nodes -->
        <div v-for="node in technologyTree.tree" :key="node.node_number" style="margin-bottom: 10px;">
          <el-card shadow="hover">
            <div style="display: flex; justify-content: space-between; align-items: start;">
              <div style="flex: 1;">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                  <el-tag size="small" style="margin-right: 8px;">{{ node.node_number }}</el-tag>
                  <strong style="font-size: 15px;">{{ node.operation.name }}</strong>
                  <el-tag size="small" type="info" style="margin-left: 8px;">{{ node.operation.number }}</el-tag>
                </div>
                
                <div style="font-size: 12px; color: #606266; margin-bottom: 8px;">
                  <el-icon><Tools /></el-icon> 
                  Workstations: {{ node.operation.workstations.join(', ') || 'None' }}
                </div>
                
                <div style="display: flex; gap: 15px; font-size: 12px; color: #909399;">
                  <span>⏱️ TJ: {{ formatTime(node.operation.tj) }}</span>
                  <span>🔧 TPZ: {{ formatTime(node.operation.tpz) }}</span>
                  <span>⏭️ Next: {{ formatTime(node.operation.time_next_operation) }}</span>
                  <span v-if="node.parent_node_number">📌 Parent: {{ node.parent_node_number }}</span>
                </div>

                <!-- Input/Output Products -->
                <div v-if="node.input_products.length > 0 || node.output_products.length > 0" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ebeef5;">
                  <div v-if="node.input_products.length > 0" style="margin-bottom: 5px;">
                    <el-tag size="small" type="warning" effect="plain">Inputs:</el-tag>
                    <span v-for="(inp, idx) in node.input_products" :key="idx" style="margin-left: 5px; font-size: 12px;">
                      {{ inp.name }} ({{ inp.quantity }})
                    </span>
                  </div>
                  <div v-if="node.output_products.length > 0">
                    <el-tag size="small" type="success" effect="plain">Outputs:</el-tag>
                    <span v-for="(out, idx) in node.output_products" :key="idx" style="margin-left: 5px; font-size: 12px;">
                      {{ out.name }} ({{ out.quantity }})
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
      <div v-else style="text-align: center; padding: 40px; color: #909399;">
        <el-icon :size="48"><Box /></el-icon>
        <div style="margin-top: 10px;">No operation tree available</div>
      </div>
    </el-dialog>

    <!-- Bulk State Change Confirmation -->
    <el-dialog v-model="showBulkStateDialog" title="Change State" width="400px">
      <p>Change state for {{ selectedTechnologies.length }} selected routings to:</p>
      <el-select v-model="bulkState" style="width: 100%; margin-top: 10px;">
        <el-option label="Draft" value="draft" />
        <el-option label="Accepted" value="accepted" />
        <el-option label="Checked" value="checked" />
        <el-option label="Outdated" value="outdated" />
        <el-option label="Declined" value="declined" />
      </el-select>
      <template #footer>
        <el-button @click="showBulkStateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="confirmBulkStateChange">Confirm</el-button>
      </template>
    </el-dialog>

    <!-- Add Operation Dialog -->
    <el-dialog v-model="showAddOperationDialog" title="Add Operation to Routing" width="600px">
      <el-form :model="operationComponentForm" label-width="150px">
        <el-form-item label="Operation" required>
          <el-select 
            v-model="operationComponentForm.operation" 
            filterable 
            placeholder="Select Operation" 
            style="width: 100%;"
            @change="onOperationSelected"
          >
            <el-option 
              v-for="op in availableOperations" 
              :key="op.id" 
              :label="`${op.number} - ${op.name}`" 
              :value="op.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Node Number" required>
          <el-input 
            v-model="operationComponentForm.node_number" 
            placeholder="e.g., 010, 020, 030"
          />
          <span style="font-size: 12px; color: #909399;">
            Use increments of 10 for proper ordering
          </span>
        </el-form-item>
        <el-form-item label="Priority">
          <el-input-number 
            v-model="operationComponentForm.priority" 
            :min="1" 
            :max="999"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="Parent Operation">
          <el-select 
            v-model="operationComponentForm.parent" 
            filterable 
            placeholder="None (Root operation)" 
            style="width: 100%;"
            clearable
          >
            <el-option 
              v-for="op in operationComponents" 
              :key="op.id" 
              :label="`${op.node_number} - ${op.operation_name}`" 
              :value="op.id" 
            />
          </el-select>
          <span style="font-size: 12px; color: #909399;">
            Leave empty for root-level operations
          </span>
        </el-form-item>
        
        <el-divider content-position="left">Time Overrides (Optional)</el-divider>
        
        <el-form-item label="TJ (seconds)">
          <el-input-number 
            v-model="operationComponentForm.tj" 
            :min="0" 
            placeholder="Leave empty to use operation default"
            style="width: 100%;"
          />
          <span style="font-size: 12px; color: #909399;">
            Time for batch. Default: {{ selectedOperationDefaults.tj || 0 }}s
          </span>
        </el-form-item>
        <el-form-item label="TPZ (seconds)">
          <el-input-number 
            v-model="operationComponentForm.tpz" 
            :min="0" 
            placeholder="Leave empty to use operation default"
            style="width: 100%;"
          />
          <span style="font-size: 12px; color: #909399;">
            Preparation time. Default: {{ selectedOperationDefaults.tpz || 0 }}s
          </span>
        </el-form-item>
        <el-form-item label="Next Op. Time (s)">
          <el-input-number 
            v-model="operationComponentForm.time_next_operation" 
            :min="0" 
            placeholder="Leave empty to use operation default"
            style="width: 100%;"
          />
          <span style="font-size: 12px; color: #909399;">
            Time to next operation. Default: {{ selectedOperationDefaults.time_next_operation || 0 }}s
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeOperationDialog">Cancel</el-button>
        <el-button type="primary" @click="saveOperationComponent" :loading="savingOperation">
          {{ editingOperationComponent ? 'Update' : 'Add' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Manage Products Dialog -->
    <el-dialog v-model="showProductsDialog" title="Manage Operation Products" width="800px" top="5vh">
      <div v-if="selectedOperationComponent">
        <h3 style="margin-top: 0;">{{ selectedOperationComponent.operation_name }}</h3>
        
        <el-tabs v-model="productsTab">
          <!-- Input Products -->
          <el-tab-pane label="Input Products" name="input">
            <div style="margin-bottom: 15px;">
              <el-button type="primary" size="small" @click="addInputProduct">
                <el-icon><Plus /></el-icon> Add Input Product
              </el-button>
            </div>
            
            <el-table :data="inputProducts" style="width: 100%;">
              <el-table-column label="Product" min-width="200">
                <template #default="scope">
                  <el-select 
                    v-model="scope.row.product" 
                    filterable 
                    placeholder="Select Product"
                    style="width: 100%;"
                    :disabled="scope.row.id !== null && scope.row.id !== undefined"
                  >
                    <el-option 
                      v-for="p in products" 
                      :key="p.id" 
                      :label="`${p.number} - ${p.name}`" 
                      :value="p.id" 
                    />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="Quantity" width="150">
                <template #default="scope">
                  <el-input-number 
                    v-model="scope.row.quantity" 
                    :min="0.00001"
                    :precision="5"
                    :step="1"
                    style="width: 100%;"
                  />
                </template>
              </el-table-column>
              <el-table-column label="Actions" width="150">
                <template #default="scope">
                  <el-button 
                    v-if="!scope.row.id" 
                    size="small" 
                    type="success" 
                    @click="saveInputProduct(scope.row, scope.$index)"
                  >
                    Save
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click="removeInputProduct(scope.row, scope.$index)"
                  >
                    Delete
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- Output Products -->
          <el-tab-pane label="Output Products" name="output">
            <div style="margin-bottom: 15px;">
              <el-button type="primary" size="small" @click="addOutputProduct">
                <el-icon><Plus /></el-icon> Add Output Product
              </el-button>
            </div>
            
            <el-table :data="outputProducts" style="width: 100%;">
              <el-table-column label="Product" min-width="200">
                <template #default="scope">
                  <el-select 
                    v-model="scope.row.product" 
                    filterable 
                    placeholder="Select Product"
                    style="width: 100%;"
                    :disabled="scope.row.id !== null && scope.row.id !== undefined"
                  >
                    <el-option 
                      v-for="p in products" 
                      :key="p.id" 
                      :label="`${p.number} - ${p.name}`" 
                      :value="p.id" 
                    />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="Quantity" width="150">
                <template #default="scope">
                  <el-input-number 
                    v-model="scope.row.quantity" 
                    :min="0.00001"
                    :precision="5"
                    :step="1"
                    style="width: 100%;"
                  />
                </template>
              </el-table-column>
              <el-table-column label="Actions" width="150">
                <template #default="scope">
                  <el-button 
                    v-if="!scope.row.id" 
                    size="small" 
                    type="success" 
                    @click="saveOutputProduct(scope.row, scope.$index)"
                  >
                    Save
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click="removeOutputProduct(scope.row, scope.$index)"
                  >
                    Delete
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  Plus, Search, ArrowDown, View, Edit, Delete, Download, 
  Check, CircleCheck, StarFilled, DocumentCopy, Share, Tools, Box, Refresh
} from '@element-plus/icons-vue';
import { 
  getRoutings as getTechnologies,
  getRoutingStats as getTechnologyStats,
  getRoutingTree as getTechnologyTree,
  createRouting as createTechnology,
  updateRouting as updateTechnology,
  deleteRouting as deleteTechnology,
  changeRoutingState as changeTechnologyState,
  bulkChangeRoutingState as bulkChangeState,
  bulkActivateRouting as bulkActivate,
  bulkDeactivateRouting as bulkDeactivate,
  bulkDeleteRouting as bulkDelete,
  setMasterRouting as setMasterTechnology,
  getRoutingOperationComponents as getTechnologyOperationComponents,
  createRoutingOperationComponent as createTechnologyOperationComponent,
  updateRoutingOperationComponent as updateTechnologyOperationComponent,
  deleteRoutingOperationComponent as deleteTechnologyOperationComponent,
  createOperationProductIn, deleteOperationProductIn,
  createOperationProductOut, deleteOperationProductOut,
  getOperations
} from '../services/routingService';
import { getProducts } from '@/modules/products/services/productsService';
import { useAuthStore } from '@/modules/auth/stores/authStore';

// Data
const technologies = ref([]);
const products = ref([]);
const stats = ref({});
const loading = ref(false);
const saving = ref(false);
const searchQuery = ref('');
const filterState = ref('');
const filterMaster = ref('');
const filterActive = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const selectedTechnologies = ref([]);

// Dialogs
const showCreateDialog = ref(false);
const showDetailsDialog = ref(false);
const showTreeDialog = ref(false);
const showBulkStateDialog = ref(false);
const showAddOperationDialog = ref(false);
const showProductsDialog = ref(false);
const activeTab = ref('basic');
const productsTab = ref('input');

// Forms
const editingTechnology = ref(null);
const selectedTech = ref(null);
const technologyTree = ref(null);
const bulkState = ref('accepted');

const technologyForm = ref({
  number: '',
  name: '',
  product: null,
  description: '',
  state: 'draft',
  master: false,
  active: true,
});

// Operations Management
const operationComponents = ref([]);
const availableOperations = ref([]);
const loadingOperations = ref(false);
const savingOperation = ref(false);
const editingOperationComponent = ref(null);
const selectedOperationComponent = ref(null);
const selectedOperationDefaults = ref({});

const operationComponentForm = ref({
  technology: null,
  operation: null,
  parent: null,
  node_number: '',
  priority: 1,
  tj: null,
  tpz: null,
  time_next_operation: null,
});

// Products Management
const inputProducts = ref([]);
const outputProducts = ref([]);

// Auth
const auth = useAuthStore();
const canEditTech = computed(() => auth.hasRole(['Supervisor', 'Admin']));

// Methods
const getStateType = (state) => {
  const types = {
    draft: 'info',
    accepted: 'success',
    checked: '',
    outdated: 'warning',
    declined: 'danger',
  };
  return types[state] || '';
};

const formatTime = (seconds) => {
  if (!seconds || seconds === 0) return '0s';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  const parts = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);
  
  return parts.join(' ');
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString();
};

const loadStats = async () => {
  try {
    stats.value = await getTechnologyStats();
  } catch (error) {
    console.error('Failed to load stats:', error);
  }
};

const loadTechnologies = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      search: searchQuery.value,
      state: filterState.value,
    };
    
    if (filterMaster.value !== '') {
      params.master = filterMaster.value === 'true';
    }
    if (filterActive.value !== '') {
      params.active = filterActive.value === 'true';
    }
    
    const data = await getTechnologies(params);
    technologies.value = data.results || data;
    total.value = data.count || technologies.value.length;
  } catch (error) {
    ElMessage.error('Failed to load routings');
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

const loadAvailableOperations = async () => {
  try {
    const data = await getOperations();
    availableOperations.value = data.results || data;
  } catch (error) {
    console.error('Failed to load operations:', error);
  }
};

const loadOperationComponents = async () => {
  if (!editingTechnology.value) return;
  
  loadingOperations.value = true;
  try {
    const data = await getTechnologyOperationComponents(editingTechnology.value.id);
    operationComponents.value = data.results || data;
  } catch (error) {
    ElMessage.error('Failed to load operations');
    console.error(error);
  } finally {
    loadingOperations.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  loadTechnologies();
};

const handleSelectionChange = (selection) => {
  selectedTechnologies.value = selection;
};

const openCreateDialog = () => {
  editingTechnology.value = null;
  technologyForm.value = {
    number: '',
    name: '',
    product: null,
    description: '',
    state: 'draft',
    master: false,
    active: true,
  };
  activeTab.value = 'basic';
  showCreateDialog.value = true;
};

const closeDialog = () => {
  showCreateDialog.value = false;
  editingTechnology.value = null;
  operationComponents.value = [];
};

const viewTechnology = async (technology) => {
  try {
    selectedTech.value = technology;
    showDetailsDialog.value = true;
  } catch (error) {
    ElMessage.error('Failed to load routing details');
  }
};

const editTechnology = async (technology) => {
  editingTechnology.value = technology;
  technologyForm.value = { 
    ...technology,
    state: technology.state || 'draft',
    active: technology.active !== false
  };
  activeTab.value = 'basic';
  showCreateDialog.value = true;
  
  // Load operations if on operations tab
  await loadOperationComponents();
};

const saveTechnology = async () => {
  if (!technologyForm.value.number || !technologyForm.value.name || !technologyForm.value.product) {
    ElMessage.warning('Please fill in required fields: Number, Name, and Product');
    return;
  }

  saving.value = true;
  try {
    if (editingTechnology.value) {
      await updateTechnology(editingTechnology.value.id, technologyForm.value);
      ElMessage.success('Routing updated successfully');
      // Update the editing reference
      editingTechnology.value = { ...editingTechnology.value, ...technologyForm.value };
    } else {
      const newTech = await createTechnology(technologyForm.value);
      ElMessage.success('Routing created successfully');
      // Set as editing so user can add operations
      editingTechnology.value = newTech;
      technologyForm.value = { ...newTech };
    }
    loadTechnologies();
    loadStats();
  } catch (error) {
    ElMessage.error('Failed to save routing');
    console.error(error);
  } finally {
    saving.value = false;
  }
};

const toggleActive = async (technology) => {
  try {
    await updateTechnology(technology.id, { active: technology.active });
    ElMessage.success(`Routing ${technology.active ? 'activated' : 'deactivated'}`);
    loadStats();
  } catch (error) {
    ElMessage.error('Failed to update routing');
    technology.active = !technology.active; // Revert on error
  }
};

const handleActionMenu = async (technology, command) => {
  switch (command) {
    case 'tree':
      await viewTree(technology);
      break;
    case 'accept':
      await changeState(technology, 'accepted');
      break;
    case 'check':
      await changeState(technology, 'checked');
      break;
    case 'setMaster':
      await setAsMaster(technology);
      break;
    case 'copy':
      await copyTechnology(technology);
      break;
    case 'delete':
      await deleteTech(technology);
      break;
  }
};

const viewTree = async (technology) => {
  try {
    technologyTree.value = await getTechnologyTree(technology.id);
    showTreeDialog.value = true;
  } catch (error) {
    ElMessage.error('Failed to load operation tree');
    console.error(error);
  }
};

const changeState = async (technology, newState) => {
  try {
    await changeTechnologyState(technology.id, newState);
    ElMessage.success(`Routing state changed to ${newState}`);
    loadTechnologies();
    loadStats();
  } catch (error) {
    ElMessage.error('Failed to change routing state');
    console.error(error);
  }
};

const setAsMaster = async (technology) => {
  try {
    await ElMessageBox.confirm(
      `Set "${technology.name}" as master routing for product "${technology.product_name}"? This will unset any existing master routing.`,
      'Set Master Routing',
      { type: 'warning' }
    );
    await setMasterTechnology(technology.id);
    ElMessage.success('Routing set as master');
    loadTechnologies();
    loadStats();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to set master routing');
    }
  }
};

const copyTechnology = async (technology) => {
  const newNumber = `${technology.number}-COPY`;
  const newName = `${technology.name} (Copy)`;
  
  try {
    await createTechnology({
      ...technology,
      id: undefined,
      number: newNumber,
      name: newName,
      master: false,
      state: 'draft'
    });
    ElMessage.success('Routing copied successfully');
    loadTechnologies();
    loadStats();
  } catch (error) {
    ElMessage.error('Failed to copy routing');
  }
};

const deleteTech = async (technology) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete routing "${technology.name}"?`,
      'Delete Routing',
      { type: 'error' }
    );
    await deleteTechnology(technology.id);
    ElMessage.success('Routing deleted');
    loadTechnologies();
    loadStats();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete routing');
    }
  }
};

const handleBulkAction = (command) => {
  if (selectedTechnologies.value.length === 0) {
    ElMessage.warning('No routings selected');
    return;
  }

  switch (command) {
    case 'accept':
    case 'check':
    case 'decline':
      bulkState.value = command === 'accept' ? 'accepted' : command === 'check' ? 'checked' : 'declined';
      showBulkStateDialog.value = true;
      break;
    case 'activate':
      bulkActivateTechnologies();
      break;
    case 'deactivate':
      bulkDeactivateTechnologies();
      break;
    case 'delete':
      bulkDeleteTechnologies();
      break;
  }
};

const confirmBulkStateChange = async () => {
  const ids = selectedTechnologies.value.map(t => t.id);
  try {
    await bulkChangeState(ids, bulkState.value);
    ElMessage.success(`${ids.length} routings updated`);
    showBulkStateDialog.value = false;
    loadTechnologies();
    loadStats();
  } catch (error) {
    ElMessage.error('Failed to update routings');
  }
};

const bulkActivateTechnologies = async () => {
  const ids = selectedTechnologies.value.map(t => t.id);
  try {
    await bulkActivate(ids);
    ElMessage.success(`${ids.length} routings activated`);
    loadTechnologies();
    loadStats();
  } catch (error) {
    ElMessage.error('Failed to activate routings');
  }
};

const bulkDeactivateTechnologies = async () => {
  const ids = selectedTechnologies.value.map(t => t.id);
  try {
    await bulkDeactivate(ids);
    ElMessage.success(`${ids.length} routings deactivated`);
    loadTechnologies();
    loadStats();
  } catch (error) {
    ElMessage.error('Failed to deactivate routings');
  }
};

const bulkDeleteTechnologies = async () => {
  const ids = selectedTechnologies.value.map(t => t.id);
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete ${ids.length} selected routings?`,
      'Bulk Delete',
      { type: 'error' }
    );
    await bulkDelete(ids);
    ElMessage.success(`${ids.length} routings deleted`);
    loadTechnologies();
    loadStats();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete routings');
    }
  }
};

const exportToCSV = () => {
  if (technologies.value.length === 0) {
    ElMessage.warning('No data to export');
    return;
  }

  const headers = ['Number', 'Name', 'Product', 'State', 'Master', 'Active'];
  const rows = technologies.value.map(tech => [
    tech.number,
    tech.name,
    tech.product_name || '',
    tech.state,
    tech.master ? 'Yes' : 'No',
    tech.active ? 'Yes' : 'No'
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `routings_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
  
  ElMessage.success('CSV exported successfully');
};

// Operations Management Methods
const onOperationSelected = () => {
  const selectedOp = availableOperations.value.find(op => op.id === operationComponentForm.value.operation);
  if (selectedOp) {
    selectedOperationDefaults.value = {
      tj: selectedOp.tj || 0,
      tpz: selectedOp.tpz || 0,
      time_next_operation: selectedOp.time_next_operation || 0
    };
  }
};

const closeOperationDialog = () => {
  showAddOperationDialog.value = false;
  editingOperationComponent.value = null;
  operationComponentForm.value = {
    technology: null,
    operation: null,
    parent: null,
    node_number: '',
    priority: 1,
    tj: null,
    tpz: null,
    time_next_operation: null,
  };
  selectedOperationDefaults.value = {};
};

const editOperationComponent = (component) => {
  editingOperationComponent.value = component;
  operationComponentForm.value = {
    technology: component.technology,
    operation: component.operation,
    parent: component.parent,
    node_number: component.node_number,
    priority: component.priority,
    tj: component.tj,
    tpz: component.tpz,
    time_next_operation: component.time_next_operation,
  };
  showAddOperationDialog.value = true;
  onOperationSelected();
};

const saveOperationComponent = async () => {
  if (!operationComponentForm.value.operation || !operationComponentForm.value.node_number) {
    ElMessage.warning('Please select an operation and enter a node number');
    return;
  }

  savingOperation.value = true;
  try {
    const formData = {
      ...operationComponentForm.value,
      technology: editingTechnology.value.id,
    };

    if (editingOperationComponent.value) {
      await updateTechnologyOperationComponent(editingOperationComponent.value.id, formData);
      ElMessage.success('Operation updated successfully');
    } else {
      await createTechnologyOperationComponent(formData);
      ElMessage.success('Operation added successfully');
    }
    
    closeOperationDialog();
    await loadOperationComponents();
  } catch (error) {
    ElMessage.error('Failed to save operation');
    console.error(error);
  } finally {
    savingOperation.value = false;
  }
};

const deleteOperationComponent = async (component) => {
  try {
    await ElMessageBox.confirm(
      `Remove operation "${component.operation_name}" from this routing?`,
      'Delete Operation',
      { type: 'warning' }
    );
    await deleteTechnologyOperationComponent(component.id);
    ElMessage.success('Operation removed');
    await loadOperationComponents();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete operation');
    }
  }
};

// Products Management Methods
const manageProducts = async (component) => {
  selectedOperationComponent.value = component;
  inputProducts.value = component.input_products || [];
  outputProducts.value = component.output_products || [];
  productsTab.value = 'input';
  showProductsDialog.value = true;
};

const addInputProduct = () => {
  inputProducts.value.push({
    operation_component: selectedOperationComponent.value.id,
    product: null,
    quantity: 1
  });
};

const addOutputProduct = () => {
  outputProducts.value.push({
    operation_component: selectedOperationComponent.value.id,
    product: null,
    quantity: 1
  });
};

const saveInputProduct = async (product, index) => {
  if (!product.product || !product.quantity) {
    ElMessage.warning('Please select a product and enter quantity');
    return;
  }

  try {
    const saved = await createOperationProductIn(product);
    inputProducts.value[index] = saved;
    ElMessage.success('Input product added');
    await loadOperationComponents();
  } catch (error) {
    ElMessage.error('Failed to add input product');
    console.error(error);
  }
};

const saveOutputProduct = async (product, index) => {
  if (!product.product || !product.quantity) {
    ElMessage.warning('Please select a product and enter quantity');
    return;
  }

  try {
    const saved = await createOperationProductOut(product);
    outputProducts.value[index] = saved;
    ElMessage.success('Output product added');
    await loadOperationComponents();
  } catch (error) {
    ElMessage.error('Failed to add output product');
    console.error(error);
  }
};

const removeInputProduct = async (product, index) => {
  try {
    if (product.id) {
      await ElMessageBox.confirm('Delete this input product?', 'Confirm', { type: 'warning' });
      await deleteOperationProductIn(product.id);
      ElMessage.success('Input product deleted');
      await loadOperationComponents();
    }
    inputProducts.value.splice(index, 1);
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete input product');
    }
  }
};

const removeOutputProduct = async (product, index) => {
  try {
    if (product.id) {
      await ElMessageBox.confirm('Delete this output product?', 'Confirm', { type: 'warning' });
      await deleteOperationProductOut(product.id);
      ElMessage.success('Output product deleted');
      await loadOperationComponents();
    }
    outputProducts.value.splice(index, 1);
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete output product');
    }
  }
};

onMounted(() => {
  loadStats();
  loadTechnologies();
  loadProducts();
  loadAvailableOperations();
});
</script>

<style scoped>
.routing {
  padding: 20px;
}

/* Stats Dashboard */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 32px;
  line-height: 1;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-total {
  border-left: 4px solid #409eff;
}

.stat-draft {
  border-left: 4px solid #909399;
}

.stat-accepted {
  border-left: 4px solid #67c23a;
}

.stat-master {
  border-left: 4px solid #f59e0b;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

/* Form Hints */
:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-dialog__body) {
  padding-top: 10px;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-container {
    grid-template-columns: 1fr;
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
  
  .stat-value {
    font-size: 24px;
  }
}

/* Tree Dialog Scrollbar */
.el-dialog__body::-webkit-scrollbar {
  width: 8px;
}

.el-dialog__body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.el-dialog__body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.el-dialog__body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
