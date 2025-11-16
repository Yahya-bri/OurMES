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

const routes = [
  { path: '/login', name: 'Login', component: LoginPage, meta: { public: true } },
  { path: '/', name: 'Dashboard', component: DashboardPage, meta: { requiresAuth: true, group: 'Dashboard' } },
  { path: '/orders', name: 'Orders', component: OrdersPage, meta: { requiresAuth: true, group: 'Orders' } },
  { path: '/products', name: 'Products', component: ProductsPage, meta: { requiresAuth: true, group: 'Production Master Data', label: 'Products', subOrder: 1 } },
  { path: '/routing', name: 'Routing', component: RoutingPage, meta: { requiresAuth: true, group: 'Production Master Data', label: 'Routing', subOrder: 2 } },
  { path: '/operations', name: 'Operations', component: OperationsPage, meta: { requiresAuth: true, group: 'Production Master Data', label: 'Operations', subOrder: 3 } },
  { path: '/companies', name: 'Companies', component: CompaniesPage, meta: { requiresAuth: true, group: 'Master Data', label: 'Companies', subOrder: 1 } },
  { path: '/staff', name: 'Staff', component: StaffPage, meta: { requiresAuth: true, group: 'Master Data', label: 'Staff', subOrder: 2 } },
  { path: '/workstations', name: 'Workstations', component: WorkstationsPage, meta: { requiresAuth: true, group: 'Production Master Data', label: 'Workstations', subOrder: 4 } },
  { path: '/production-lines', name: 'ProductionLines', component: ProductionLinesPage, meta: { requiresAuth: true, group: 'Production Master Data', label: 'Production Lines', subOrder: 5 } },
  { path: '/production', name: 'Production', component: ProductionOverviewPage, meta: { requiresAuth: true, group: 'Production', label: 'Overview', subOrder: 1 } },
  { path: '/scheduling', name: 'Scheduling', component: SchedulingPage, meta: { requiresAuth: true, group: 'Production', label: 'Scheduling', subOrder: 2 } },
  { path: '/operator', name: 'Operator', component: OperatorConsolePage, meta: { requiresAuth: true, group: 'Production', label: 'Operator Console', subOrder: 5 } },
  { path: '/reports', name: 'Reports', component: ReportsPage, meta: { requiresAuth: true, group: 'Reports' } },
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
