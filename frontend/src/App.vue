<template>
  <el-container class="app-shell">
    <!-- Sidebar: Services -->
    <el-aside width="220px" class="app-aside">
      <div class="brand">OurMES</div>
      <el-menu
        :default-active="currentGroupKey"
        class="aside-menu"
        @select="onGroupSelect"
      >
        <el-menu-item v-for="grp in groups" :key="grp.key" :index="grp.key">
          <el-icon><component :is="grp.icon" /></el-icon>
          <span>{{ grp.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- Header: Sub-services of selected group (only if multiple) -->
      <el-header class="sub-header" v-if="currentGroupRoutes.length > 1">
        <div class="subnav">
          <el-menu
            mode="horizontal"
            :default-active="$route.path"
            :ellipsis="false"
            @select="onMenuSelect"
          >
            <el-menu-item
              v-for="item in currentGroupRoutes"
              :key="item.path"
              :index="item.path"
            >
              {{ item.label || item.name }}
            </el-menu-item>
          </el-menu>
        </div>
        <div class="auth-controls">
          <template v-if="isAuthenticated">
            <span class="user-chip"
              >{{ user?.username }} ({{ roles.join(", ") }})</span
            >
            <el-button link type="danger" @click="onLogout">Logout</el-button>
          </template>
          <template v-else>
            <el-button link type="primary" @click="router.push('/login')"
              >Login</el-button
            >
          </template>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { storeToRefs } from "pinia";
import { useAuthStore } from "@/modules/auth/stores/authStore";
import {
  House,
  Tools,
  UserFilled,
  VideoPlay,
  Menu,
} from "@element-plus/icons-vue";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const { user, roles, isAuthenticated } = storeToRefs(auth);

function onMenuSelect(index) {
  router.push(index);
}

function onLogout() {
  auth.logout();
  router.push("/login");
}

// Define Role Icons
const ROLE_ICONS = {
  "Plant Manager": House,
  "Manufacturing Engineer": Tools,
  "Production Supervisor": UserFilled,
  Operator: VideoPlay,
  Other: Menu,
};

// Build groups from router meta (each page belongs to a role)
const groups = computed(() => {
  const map = new Map();
  router.getRoutes().forEach((r) => {
    if (r.meta && r.meta.requiresAuth && r.meta.role) {
      const role = r.meta.role;
      const list = map.get(role) || [];
      list.push({
        path: r.path,
        name: r.name,
        label: r.meta?.label || r.name,
      });
      map.set(role, list);
    }
  });

  // Define the order of roles in the sidebar
  const ROLE_ORDER = [
    "Plant Manager",
    "Manufacturing Engineer",
    "Production Supervisor",
    "Operator",
  ];

  return ROLE_ORDER.filter((role) => map.has(role)).map((role) => {
    const routes = map
      .get(role)
      .slice()
      .sort((a, b) => a.label.localeCompare(b.label));
    return { key: role, label: role, icon: ROLE_ICONS[role] || Menu, routes };
  });
});

const currentGroupKey = computed(
  () => route.meta.role || groups.value[0]?.key || ""
);
const currentGroupRoutes = computed(() => {
  const grp = groups.value.find((g) => g.key === currentGroupKey.value);
  return grp ? grp.routes : [];
});

function onGroupSelect(groupKey) {
  const grp = groups.value.find((g) => g.key === groupKey);
  if (grp && grp.routes.length) {
    router.push(grp.routes[0].path);
  }
}
</script>

<style>
body {
  margin: 0;
  font-family: "Inter", "Roboto", Arial, sans-serif;
}

.app-shell {
  min-height: 100vh;
}
.app-aside {
  border-right: 1px solid #ebeef5;
  background: #fff;
}
.brand {
  font-weight: 700;
  font-size: 18px;
  padding: 16px;
  color: #303133;
}
.aside-menu {
  border-right: none;
}
.sub-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  height: 56px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  background: #fff;
}
.subnav .el-menu {
  border-bottom: none;
  flex-wrap: wrap;
}
.auth-controls {
  padding-right: 12px;
}
.user-chip {
  margin-right: 8px;
  color: #666;
}
.el-main {
  background-color: #f5f7fa;
}
</style>
