import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/modules/auth/stores/authStore';

const DashboardPage = () => import('@/modules/dashboard/pages/DashboardPage.vue');
const OrdersPage = () => import('@/modules/orders/pages/OrdersPage.vue');
const ProductsPage = () => import('@/modules/products/pages/ProductsPage.vue');
const RoutingPage = () => import('@/modules/routing/pages/RoutingPage.vue');
const OperationsPage = () => import('@/modules/routing/pages/OperationsPage.vue');
const CompaniesPage = () => import('@/modules/basic-data/pages/CompaniesPage.vue');
const StaffPage = () => import('@/modules/basic-data/pages/StaffPage.vue');
const WorkstationsPage = () => import('@/modules/basic-data/pages/WorkstationsPage.vue');
const ProductionLinesPage = () => import('@/modules/basic-data/pages/ProductionLinesPage.vue');
const ProductionOverviewPage = () => import('@/modules/production/pages/ProductionOverviewPage.vue');
const SchedulingPage = () => import('@/modules/planning/pages/SchedulingPage.vue');
const OperatorConsolePage = () => import('@/modules/production/pages/OperatorConsolePage.vue');
const ReportsPage = () => import('@/modules/reports/pages/ReportsPage.vue');
const LoginPage = () => import('@/modules/auth/pages/LoginPage.vue');
const InventoryPage = () => import('@/modules/inventory/pages/InventoryPage.vue');
const TraceabilityPage = () => import('@/modules/inventory/pages/TraceabilityPage.vue');
const MaterialSyncPage = () => import('@/modules/inventory/pages/MaterialSyncPage.vue');
const MaintenanceDashboard = () => import('@/modules/maintenance/pages/MaintenanceDashboard.vue');
const SPCPage = () => import('@/modules/quality/pages/SPCPage.vue');
const NCRPage = () => import('@/modules/quality/pages/NCRPage.vue');
const InspectionConfigPage = () => import('@/modules/quality/pages/InspectionConfigPage.vue');

const routes = [
  { path: '/login', name: 'Login', component: LoginPage, meta: { public: true } },
  
  // Plant Manager
  { path: '/', name: 'Dashboard', component: DashboardPage, meta: { requiresAuth: true, role: 'Plant Manager', label: 'Dashboard', subOrder: 1 } },
  { path: '/reports', name: 'Reports', component: ReportsPage, meta: { requiresAuth: true, role: 'Plant Manager', label: 'Compliance Reports', subOrder: 2 } },
  { path: '/staff', name: 'Staff', component: StaffPage, meta: { requiresAuth: true, role: 'Plant Manager', label: 'Staff Management', subOrder: 3 } },
  { path: '/companies', name: 'Companies', component: CompaniesPage, meta: { requiresAuth: true, role: 'Plant Manager', label: 'Companies', subOrder: 4 } },

  // Manufacturing Engineer
  { path: '/products', name: 'Products', component: ProductsPage, meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Product Definitions', subOrder: 1 } },
  { path: '/routing', name: 'Routing', component: RoutingPage, meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Routings', subOrder: 2 } },
  { path: '/operations', name: 'Operations', component: OperationsPage, meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Operations Library', subOrder: 3 } },
  { path: '/workstations', name: 'Workstations', component: WorkstationsPage, meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Workstations', subOrder: 4 } },
  { path: '/production-lines', name: 'ProductionLines', component: ProductionLinesPage, meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Production Lines', subOrder: 5 } },
  { path: '/data-collection-config', name: 'DataCollectionConfig', component: () => import('@/modules/production/pages/DataCollectionConfigPage.vue'), meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Data Collection', subOrder: 6 } },
  { path: '/root-cause', name: 'RootCauseAnalysis', component: () => import('@/modules/reports/pages/RootCauseAnalysisPage.vue'), meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Root Cause Analysis', subOrder: 7 } },
  // New Maintenance & Quality Routes for Engineer
  { path: '/maintenance', name: 'Maintenance', component: () => import('@/modules/maintenance/pages/MaintenanceDashboard.vue'), meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Maintenance', subOrder: 8 } },
  { path: '/spc', name: 'SPC', component: () => import('@/modules/quality/pages/SPCPage.vue'), meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'SPC Charts', subOrder: 9 } },
  { path: '/ncr', name: 'NCR', component: () => import('@/modules/quality/pages/NCRPage.vue'), meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'NCR Management', subOrder: 10 } },
  { path: '/inspection-config', name: 'InspectionConfig', component: () => import('@/modules/quality/pages/InspectionConfigPage.vue'), meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Inspection Config', subOrder: 11 } },
  { path: '/traceability', name: 'Traceability', component: () => import('@/modules/inventory/pages/TraceabilityPage.vue'), meta: { requiresAuth: true, role: 'Manufacturing Engineer', label: 'Traceability', subOrder: 12 } },

  // Production Supervisor
  { path: '/scheduling', name: 'Scheduling', component: SchedulingPage, meta: { requiresAuth: true, role: 'Production Supervisor', label: 'Scheduling', subOrder: 1 } },
  { path: '/dispatching', name: 'Dispatching', component: () => import('@/modules/production/pages/DispatchingPage.vue'), meta: { requiresAuth: true, role: 'Production Supervisor', label: 'Dispatching', subOrder: 2 } },
  { path: '/production-overview', name: 'ProductionOverview', component: ProductionOverviewPage, meta: { requiresAuth: true, role: 'Production Supervisor', label: 'Production Overview', subOrder: 3 } },
  { path: '/orders', name: 'Orders', component: OrdersPage, meta: { requiresAuth: true, role: 'Production Supervisor', label: 'Orders', subOrder: 4 } },
  // New Inventory Routes for Supervisor
  { path: '/inventory', name: 'Inventory', component: () => import('@/modules/inventory/pages/InventoryPage.vue'), meta: { requiresAuth: true, role: 'Production Supervisor', label: 'Inventory Visibility', subOrder: 5 } },
  { path: '/material-sync', name: 'MaterialSync', component: () => import('@/modules/inventory/pages/MaterialSyncPage.vue'), meta: { requiresAuth: true, role: 'Production Supervisor', label: 'Material Sync (Kanban)', subOrder: 6 } },

  // Operator
  { path: '/operator-console', name: 'OperatorConsole', component: OperatorConsolePage, meta: { requiresAuth: true, role: 'Operator', label: 'Operator Console', subOrder: 1 } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();
  const isPublic = to.meta && to.meta.public === true;
  if (!isPublic && !auth.isAuthenticated) {
    return next({ name: 'Login', query: { next: to.fullPath } });
  }
  if (to.name === 'Login' && auth.isAuthenticated) {
    return next({ path: '/' });
  }
  if (auth.isAuthenticated && !auth.user) {
    await auth.fetchMe().catch(() => {});
  }
  return next();
});

export default router;
