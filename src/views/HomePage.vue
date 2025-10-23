<!-- @format -->

<template>
    <ion-page>
        <ion-header :translucent="true">
            <ion-toolbar color="primary">
                <ion-title
                    >购物评论情感分析系统</ion-title
                >
            </ion-toolbar>
        </ion-header>

        <ion-content
            :fullscreen="true"
            class="ion-padding">
            <!-- 配置面板 -->
            <ion-card>
                <ion-card-header>
                    <ion-card-title
                        >分析配置</ion-card-title
                    >
                </ion-card-header>
                <ion-card-content>
                    <!-- 文件上传 -->
                    <div class="upload-section">
                        <ion-label
                            position="stacked"
                            >上传评论CSV文件</ion-label
                        >
                        <input
                            type="file"
                            accept=".csv"
                            @change="
                                handleFileSelect
                            "
                            ref="fileInput"
                            class="file-input" />
                        <ion-button
                            @click="
                                triggerFileInput
                            "
                            expand="block"
                            fill="outline">
                            <ion-icon
                                slot="start"
                                :icon="
                                    documentTextOutline
                                "></ion-icon>
                            {{
                                selectedFile
                                    ? selectedFile.name
                                    : "选择CSV文件"
                            }}
                        </ion-button>
                        <ion-note
                            v-if="selectedFile"
                            color="success">
                            文件已选择:
                            {{
                                selectedFile.name
                            }}
                            ({{
                                formatFileSize(
                                    selectedFile.size
                                )
                            }})
                        </ion-note>
                    </div>

                    <!-- 语言选择 -->
                    <div class="config-section">
                        <ion-label
                            >分析语言</ion-label
                        >
                        <ion-segment
                            v-model="
                                config.language
                            ">
                            <ion-segment-button
                                value="zh">
                                <ion-label
                                    >中文</ion-label
                                >
                            </ion-segment-button>
                            <ion-segment-button
                                value="en">
                                <ion-label
                                    >英文</ion-label
                                >
                            </ion-segment-button>
                        </ion-segment>
                    </div>

                    <!-- 特征工程选择 -->
                    <div class="config-section">
                        <ion-label
                            >特征工程方法(可多选)</ion-label
                        >
                        <ion-list>
                            <ion-item
                                v-for="feature in availableFeatures"
                                :key="
                                    feature.value
                                ">
                                <ion-checkbox
                                    slot="start"
                                    :value="
                                        feature.value
                                    "
                                    @ionChange="
                                        toggleFeature(
                                            feature.value,
                                            $event
                                        )
                                    "
                                    :checked="
                                        config.features.includes(
                                            feature.value
                                        )
                                    "></ion-checkbox>
                                <ion-label>{{
                                    feature.label
                                }}</ion-label>
                            </ion-item>
                        </ion-list>
                    </div>

                    <!-- 模型集成 -->
                    <div class="config-section">
                        <ion-item>
                            <ion-label
                                >使用模型集成</ion-label
                            >
                            <ion-toggle
                                v-model="
                                    config.useEnsemble
                                "></ion-toggle>
                        </ion-item>
                        <ion-note
                            v-if="
                                config.useEnsemble
                            "
                            color="medium">
                            将使用投票和堆叠集成方法提高准确率
                        </ion-note>
                    </div>

                    <!-- 分析按钮 -->
                    <ion-button
                        @click="analyzeComments"
                        expand="block"
                        :disabled="
                            !selectedFile ||
                            analyzing
                        "
                        class="analyze-btn">
                        <ion-icon
                            slot="start"
                            :icon="
                                analyticsOutline
                            "></ion-icon>
                        {{
                            analyzing
                                ? "分析中..."
                                : "开始分析"
                        }}
                    </ion-button>
                </ion-card-content>
            </ion-card>

            <!-- 进度条 -->
            <ion-card v-if="analyzing">
                <ion-card-content>
                    <ion-progress-bar
                        type="indeterminate"></ion-progress-bar>
                    <p class="text-center">
                        正在分析评论数据,请稍候...
                    </p>
                </ion-card-content>
            </ion-card>

            <!-- 文件统计信息 -->
            <ion-card
                v-if="
                    results && results.file_stats
                ">
                <ion-card-header>
                    <ion-card-title
                        >📊
                        文件统计信息</ion-card-title
                    >
                </ion-card-header>
                <ion-card-content>
                    <ion-list>
                        <ion-item>
                            <ion-label>
                                <h3>文件名</h3>
                                <p>
                                    {{
                                        results
                                            .file_stats
                                            .filename
                                    }}
                                </p>
                            </ion-label>
                        </ion-item>
                        <ion-item>
                            <ion-label>
                                <h3>总行数</h3>
                                <p>
                                    {{
                                        results
                                            .file_stats
                                            .total_rows
                                    }}
                                    条评论
                                </p>
                            </ion-label>
                        </ion-item>
                        <ion-item>
                            <ion-label>
                                <h3>数据列</h3>
                                <p>
                                    {{
                                        results.file_stats.columns.join(
                                            ", "
                                        )
                                    }}
                                </p>
                            </ion-label>
                        </ion-item>
                        <ion-item
                            v-if="
                                results.file_stats
                                    .product_categories
                            ">
                            <ion-label>
                                <h3>
                                    产品类别分布
                                </h3>
                                <div
                                    class="category-chips">
                                    <ion-chip
                                        v-for="(
                                            count,
                                            category
                                        ) in results
                                            .file_stats
                                            .product_categories"
                                        :key="
                                            category
                                        "
                                        color="primary">
                                        <ion-label
                                            >{{
                                                category
                                            }}:
                                            {{
                                                count
                                            }}</ion-label
                                        >
                                    </ion-chip>
                                </div>
                            </ion-label>
                        </ion-item>
                        <ion-item
                            v-if="
                                results.file_stats
                                    .price_stats
                            ">
                            <ion-label>
                                <h3>价格统计</h3>
                                <p>
                                    最低: ¥{{
                                        results.file_stats.price_stats.min.toFixed(
                                            2
                                        )
                                    }}
                                    | 最高: ¥{{
                                        results.file_stats.price_stats.max.toFixed(
                                            2
                                        )
                                    }}
                                    | 平均: ¥{{
                                        results.file_stats.price_stats.avg.toFixed(
                                            2
                                        )
                                    }}
                                </p>
                            </ion-label>
                        </ion-item>
                        <ion-item
                            v-if="
                                results.file_stats
                                    .has_date
                            ">
                            <ion-label>
                                <h3>时间范围</h3>
                                <p
                                    v-if="
                                        results.time_stats
                                    ">
                                    {{
                                        results
                                            .time_stats
                                            .date_range
                                            .start
                                    }}
                                    至
                                    {{
                                        results
                                            .time_stats
                                            .date_range
                                            .end
                                    }}
                                </p>
                            </ion-label>
                        </ion-item>
                        <ion-item
                            v-if="
                                results.file_stats
                                    .has_location
                            ">
                            <ion-label>
                                <h3>地域分布</h3>
                                <p
                                    v-if="
                                        results.location_stats
                                    ">
                                    涵盖
                                    {{
                                        results
                                            .location_stats
                                            .total_locations
                                    }}
                                    个地区
                                </p>
                            </ion-label>
                        </ion-item>
                    </ion-list>
                </ion-card-content>
            </ion-card>

            <!-- 情感分析统计结果 -->
            <ion-card
                v-if="
                    results && results.statistics
                ">
                <ion-card-header>
                    <ion-card-title
                        >分析统计</ion-card-title
                    >
                </ion-card-header>
                <ion-card-content>
                    <div class="statistics-grid">
                        <div class="stat-item">
                            <div
                                class="stat-value">
                                {{
                                    results
                                        .statistics
                                        .total
                                }}
                            </div>
                            <div
                                class="stat-label">
                                评论总数
                            </div>
                        </div>
                        <div
                            class="stat-item positive">
                            <div
                                class="stat-value">
                                {{
                                    results
                                        .statistics
                                        .counts
                                        .positive
                                }}
                            </div>
                            <div
                                class="stat-label">
                                正面 ({{
                                    results
                                        .statistics
                                        .percentages
                                        .positive
                                }}%)
                            </div>
                        </div>
                        <div
                            class="stat-item neutral">
                            <div
                                class="stat-value">
                                {{
                                    results
                                        .statistics
                                        .counts
                                        .neutral
                                }}
                            </div>
                            <div
                                class="stat-label">
                                中性 ({{
                                    results
                                        .statistics
                                        .percentages
                                        .neutral
                                }}%)
                            </div>
                        </div>
                        <div
                            class="stat-item negative">
                            <div
                                class="stat-value">
                                {{
                                    results
                                        .statistics
                                        .counts
                                        .negative
                                }}
                            </div>
                            <div
                                class="stat-label">
                                负面 ({{
                                    results
                                        .statistics
                                        .percentages
                                        .negative
                                }}%)
                            </div>
                        </div>
                    </div>

                    <!-- 基础统计图表 -->
                    <div
                        ref="pieChart"
                        class="chart-container"></div>
                    <div
                        ref="barChart"
                        class="chart-container"></div>
                </ion-card-content>
            </ion-card>

            <!-- 时间维度分析 -->
            <ion-card
                v-if="
                    results && results.time_stats
                ">
                <ion-card-header>
                    <ion-card-title
                        >📈
                        时间维度情感分析</ion-card-title
                    >
                </ion-card-header>
                <ion-card-content>
                    <div
                        ref="timeLineChart"
                        class="chart-container-large"></div>
                    <div
                        ref="timeStackChart"
                        class="chart-container-large"></div>
                </ion-card-content>
            </ion-card>

            <!-- 地域维度分析 -->
            <ion-card
                v-if="
                    results &&
                    results.location_stats
                ">
                <ion-card-header>
                    <ion-card-title
                        >🗺️
                        地域维度情感分析</ion-card-title
                    >
                </ion-card-header>
                <ion-card-content>
                    <div
                        ref="locationBarChart"
                        class="chart-container-large"></div>
                    <div
                        ref="locationMapChart"
                        class="chart-container-large"></div>
                </ion-card-content>
            </ion-card>

            <!-- 详细结果列表 -->
            <ion-card
                v-if="results && results.results">
                <ion-card-header>
                    <ion-card-title
                        >详细分析结果</ion-card-title
                    >
                    <ion-button
                        @click="exportResults"
                        size="small"
                        fill="outline">
                        <ion-icon
                            slot="start"
                            :icon="
                                downloadOutline
                            "></ion-icon>
                        导出结果
                    </ion-button>
                </ion-card-header>
                <ion-card-content>
                    <ion-list>
                        <ion-item
                            v-for="(
                                item, index
                            ) in paginatedResults"
                            :key="index">
                            <ion-label
                                class="result-item">
                                <h3>
                                    {{
                                        item.text
                                    }}
                                </h3>
                                <div
                                    class="sentiment-info">
                                    <ion-badge
                                        :color="
                                            getSentimentColor(
                                                item.sentiment
                                            )
                                        ">
                                        {{
                                            getSentimentLabel(
                                                item.sentiment
                                            )
                                        }}
                                    </ion-badge>
                                    <span
                                        class="probabilities">
                                        正面:
                                        {{
                                            (
                                                item
                                                    .probabilities
                                                    .positive *
                                                100
                                            ).toFixed(
                                                1
                                            )
                                        }}% |
                                        中性:
                                        {{
                                            (
                                                item
                                                    .probabilities
                                                    .neutral *
                                                100
                                            ).toFixed(
                                                1
                                            )
                                        }}% |
                                        负面:
                                        {{
                                            (
                                                item
                                                    .probabilities
                                                    .negative *
                                                100
                                            ).toFixed(
                                                1
                                            )
                                        }}%
                                    </span>
                                </div>
                            </ion-label>
                        </ion-item>
                    </ion-list>

                    <!-- 分页 -->
                    <div
                        class="pagination"
                        v-if="totalPages > 1">
                        <ion-button
                            size="small"
                            @click="currentPage--"
                            :disabled="
                                currentPage === 1
                            ">
                            上一页
                        </ion-button>
                        <span class="page-info"
                            >{{ currentPage }} /
                            {{ totalPages }}</span
                        >
                        <ion-button
                            size="small"
                            @click="currentPage++"
                            :disabled="
                                currentPage ===
                                totalPages
                            ">
                            下一页
                        </ion-button>
                    </div>
                </ion-card-content>
            </ion-card>

            <!-- 错误提示 -->
            <ion-toast
                :is-open="showToast"
                :message="toastMessage"
                :duration="3000"
                :color="toastColor"
                @didDismiss="
                    showToast = false
                "></ion-toast>
        </ion-content>
    </ion-page>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import {
    IonContent,
    IonHeader,
    IonPage,
    IonTitle,
    IonToolbar,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonLabel,
    IonButton,
    IonIcon,
    IonSegment,
    IonSegmentButton,
    IonList,
    IonItem,
    IonCheckbox,
    IonToggle,
    IonNote,
    IonProgressBar,
    IonBadge,
    IonToast,
    IonChip,
} from "@ionic/vue";
import {
    documentTextOutline,
    analyticsOutline,
    downloadOutline,
} from "ionicons/icons";
import * as echarts from "echarts";
import axios from "axios";

// API配置
const API_BASE_URL = "http://localhost:5000/api";

// 数据定义
const selectedFile = ref<File | null>(null);
const fileInput = ref<HTMLInputElement | null>(
    null
);
const analyzing = ref(false);
const results = ref<any>(null);
const showToast = ref(false);
const toastMessage = ref("");
const toastColor = ref("success");
const pieChart = ref<HTMLElement | null>(null);
const barChart = ref<HTMLElement | null>(null);
const timeLineChart = ref<HTMLElement | null>(
    null
);
const timeStackChart = ref<HTMLElement | null>(
    null
);
const locationBarChart = ref<HTMLElement | null>(
    null
);
const locationMapChart = ref<HTMLElement | null>(
    null
);
const currentPage = ref(1);
const pageSize = 10;

// 配置选项
const config = ref({
    language: "zh",
    features: ["basic", "sentiment_dict"],
    useEnsemble: false,
});

const availableFeatures = ref([
    { value: "basic", label: "基础词袋特征" },
    { value: "ngram", label: "N-gram特征" },
    { value: "char", label: "字符级特征" },
    {
        value: "sentiment_dict",
        label: "情感词典特征",
    },
    { value: "tfidf", label: "TF-IDF特征" },
]);

// 计算属性
const paginatedResults = computed(() => {
    if (!results.value || !results.value.results)
        return [];
    const start =
        (currentPage.value - 1) * pageSize;
    const end = start + pageSize;
    return results.value.results.slice(
        start,
        end
    );
});

const totalPages = computed(() => {
    if (!results.value || !results.value.results)
        return 0;
    return Math.ceil(
        results.value.results.length / pageSize
    );
});

// 方法
const triggerFileInput = () => {
    fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
    const target =
        event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
        selectedFile.value = target.files[0];
    }
};

const formatFileSize = (
    bytes: number
): string => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024)
        return (bytes / 1024).toFixed(2) + " KB";
    return (
        (bytes / (1024 * 1024)).toFixed(2) + " MB"
    );
};

const toggleFeature = (
    value: string,
    event: any
) => {
    if (event.detail.checked) {
        if (
            !config.value.features.includes(value)
        ) {
            config.value.features.push(value);
        }
    } else {
        config.value.features =
            config.value.features.filter(
                (f) => f !== value
            );
    }
};

const analyzeComments = async () => {
    if (!selectedFile.value) {
        showMessage("请先选择CSV文件", "warning");
        return;
    }

    if (config.value.features.length === 0) {
        showMessage(
            "请至少选择一种特征工程方法",
            "warning"
        );
        return;
    }

    analyzing.value = true;

    try {
        const formData = new FormData();
        formData.append(
            "file",
            selectedFile.value
        );
        formData.append(
            "language",
            config.value.language
        );
        formData.append(
            "use_ensemble",
            config.value.useEnsemble.toString()
        );

        config.value.features.forEach(
            (feature) => {
                formData.append(
                    "features[]",
                    feature
                );
            }
        );

        const response = await axios.post(
            `${API_BASE_URL}/analyze`,
            formData,
            {
                headers: {
                    "Content-Type":
                        "multipart/form-data",
                },
            }
        );

        results.value = response.data;
        currentPage.value = 1;

        showMessage("分析完成!", "success");

        // 延迟渲染图表,确保DOM已更新
        setTimeout(() => {
            renderCharts();
        }, 100);
    } catch (error: any) {
        console.error("分析失败:", error);

        let errorMessage =
            "分析失败,请检查文件格式";

        // 检查是否是网络错误
        if (
            error.message === "Network Error" ||
            error.code === "ERR_NETWORK"
        ) {
            errorMessage =
                "网络连接失败! 请确保:\n1. 后端服务正在运行 (http://localhost:5000)\n2. 检查CORS配置\n3. 查看浏览器控制台获取详细信息";
        } else if (error.response) {
            // 服务器返回了错误响应
            errorMessage =
                error.response.data?.error ||
                `服务器错误: ${error.response.status}`;
        } else if (error.request) {
            // 请求已发送但没有收到响应
            errorMessage =
                "服务器无响应,请确保后端服务正在运行";
        }

        showMessage(errorMessage, "danger");
    } finally {
        analyzing.value = false;
    }
};

const renderCharts = () => {
    if (
        !results.value ||
        !results.value.statistics
    )
        return;

    // 饼图
    if (pieChart.value) {
        const pie = echarts.init(pieChart.value);
        const pieOption = {
            title: {
                text: "情感分布饼图",
                left: "center",
            },
            tooltip: {
                trigger: "item",
                formatter:
                    "{a} <br/>{b}: {c} ({d}%)",
            },
            legend: {
                orient: "vertical",
                left: "left",
            },
            series: [
                {
                    name: "情感分类",
                    type: "pie",
                    radius: "50%",
                    data: [
                        {
                            value: results.value
                                .statistics.counts
                                .positive,
                            name: "正面",
                            itemStyle: {
                                color: "#10dc60",
                            },
                        },
                        {
                            value: results.value
                                .statistics.counts
                                .neutral,
                            name: "中性",
                            itemStyle: {
                                color: "#ffce00",
                            },
                        },
                        {
                            value: results.value
                                .statistics.counts
                                .negative,
                            name: "负面",
                            itemStyle: {
                                color: "#f04141",
                            },
                        },
                    ],
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor:
                                "rgba(0, 0, 0, 0.5)",
                        },
                    },
                },
            ],
        };
        pie.setOption(pieOption);
    }

    // 柱状图
    if (barChart.value) {
        const bar = echarts.init(barChart.value);
        const stats = results.value.statistics;
        const barOption = {
            title: {
                text: "平均情感概率分布",
                left: "center",
            },
            tooltip: {
                trigger: "axis",
                axisPointer: {
                    type: "shadow",
                },
            },
            xAxis: {
                type: "category",
                data: ["正面", "中性", "负面"],
            },
            yAxis: {
                type: "value",
                max: 1,
                axisLabel: {
                    formatter: "{value}",
                },
            },
            series: [
                {
                    name: "平均概率",
                    type: "bar",
                    data: [
                        {
                            value: stats
                                .average_probabilities
                                .positive,
                            itemStyle: {
                                color: "#10dc60",
                            },
                        },
                        {
                            value: stats
                                .average_probabilities
                                .neutral,
                            itemStyle: {
                                color: "#ffce00",
                            },
                        },
                        {
                            value: stats
                                .average_probabilities
                                .negative,
                            itemStyle: {
                                color: "#f04141",
                            },
                        },
                    ],
                    label: {
                        show: true,
                        position: "top",
                        formatter: "{c}",
                    },
                },
            ],
        };
        bar.setOption(barOption);
    }

    // 时间趋势折线图
    if (
        timeLineChart.value &&
        results.value.time_stats
    ) {
        const timeLine = echarts.init(
            timeLineChart.value
        );
        const timeStats =
            results.value.time_stats;

        const timeLineOption = {
            title: {
                text: "情感趋势分析（时间维度）",
                left: "center",
            },
            tooltip: {
                trigger: "axis",
            },
            legend: {
                data: ["正面", "中性", "负面"],
                top: "10%",
            },
            grid: {
                left: "3%",
                right: "4%",
                bottom: "10%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                boundaryGap: false,
                data: timeStats.dates,
                axisLabel: {
                    rotate: 45,
                },
            },
            yAxis: {
                type: "value",
                name: "评论数量",
            },
            series: [
                {
                    name: "正面",
                    type: "line",
                    data: timeStats.dates.map(
                        (date: string) =>
                            timeStats
                                .sentiment_by_date[
                                date
                            ].positive
                    ),
                    smooth: true,
                    itemStyle: {
                        color: "#10dc60",
                    },
                },
                {
                    name: "中性",
                    type: "line",
                    data: timeStats.dates.map(
                        (date: string) =>
                            timeStats
                                .sentiment_by_date[
                                date
                            ].neutral
                    ),
                    smooth: true,
                    itemStyle: {
                        color: "#ffce00",
                    },
                },
                {
                    name: "负面",
                    type: "line",
                    data: timeStats.dates.map(
                        (date: string) =>
                            timeStats
                                .sentiment_by_date[
                                date
                            ].negative
                    ),
                    smooth: true,
                    itemStyle: {
                        color: "#f04141",
                    },
                },
            ],
        };
        timeLine.setOption(timeLineOption);
    }

    // 时间堆叠面积图
    if (
        timeStackChart.value &&
        results.value.time_stats
    ) {
        const timeStack = echarts.init(
            timeStackChart.value
        );
        const timeStats =
            results.value.time_stats;

        const timeStackOption = {
            title: {
                text: "情感占比分析（时间维度）",
                left: "center",
            },
            tooltip: {
                trigger: "axis",
                axisPointer: {
                    type: "cross",
                },
            },
            legend: {
                data: ["正面", "中性", "负面"],
                top: "10%",
            },
            grid: {
                left: "3%",
                right: "4%",
                bottom: "10%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: timeStats.dates,
                axisLabel: {
                    rotate: 45,
                },
            },
            yAxis: {
                type: "value",
                name: "占比",
            },
            series: [
                {
                    name: "正面",
                    type: "bar",
                    stack: "total",
                    data: timeStats.dates.map(
                        (date: string) => {
                            const s =
                                timeStats
                                    .sentiment_by_date[
                                    date
                                ];
                            const total =
                                s.positive +
                                s.neutral +
                                s.negative;
                            return total > 0
                                ? (
                                      (s.positive /
                                          total) *
                                      100
                                  ).toFixed(1)
                                : 0;
                        }
                    ),
                    itemStyle: {
                        color: "#10dc60",
                    },
                },
                {
                    name: "中性",
                    type: "bar",
                    stack: "total",
                    data: timeStats.dates.map(
                        (date: string) => {
                            const s =
                                timeStats
                                    .sentiment_by_date[
                                    date
                                ];
                            const total =
                                s.positive +
                                s.neutral +
                                s.negative;
                            return total > 0
                                ? (
                                      (s.neutral /
                                          total) *
                                      100
                                  ).toFixed(1)
                                : 0;
                        }
                    ),
                    itemStyle: {
                        color: "#ffce00",
                    },
                },
                {
                    name: "负面",
                    type: "bar",
                    stack: "total",
                    data: timeStats.dates.map(
                        (date: string) => {
                            const s =
                                timeStats
                                    .sentiment_by_date[
                                    date
                                ];
                            const total =
                                s.positive +
                                s.neutral +
                                s.negative;
                            return total > 0
                                ? (
                                      (s.negative /
                                          total) *
                                      100
                                  ).toFixed(1)
                                : 0;
                        }
                    ),
                    itemStyle: {
                        color: "#f04141",
                    },
                },
            ],
        };
        timeStack.setOption(timeStackOption);
    }

    // 地域情感分布柱状图
    if (
        locationBarChart.value &&
        results.value.location_stats
    ) {
        const locationBar = echarts.init(
            locationBarChart.value
        );
        const locationStats =
            results.value.location_stats;

        const locationBarOption = {
            title: {
                text: "各地区情感分布",
                left: "center",
            },
            tooltip: {
                trigger: "axis",
                axisPointer: {
                    type: "shadow",
                },
            },
            legend: {
                data: ["正面", "中性", "负面"],
                top: "10%",
            },
            grid: {
                left: "3%",
                right: "4%",
                bottom: "15%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: locationStats.locations,
                axisLabel: {
                    rotate: 45,
                },
            },
            yAxis: {
                type: "value",
                name: "评论数量",
            },
            series: [
                {
                    name: "正面",
                    type: "bar",
                    data: locationStats.locations.map(
                        (loc: string) =>
                            locationStats
                                .sentiment_by_location[
                                loc
                            ].positive
                    ),
                    itemStyle: {
                        color: "#10dc60",
                    },
                },
                {
                    name: "中性",
                    type: "bar",
                    data: locationStats.locations.map(
                        (loc: string) =>
                            locationStats
                                .sentiment_by_location[
                                loc
                            ].neutral
                    ),
                    itemStyle: {
                        color: "#ffce00",
                    },
                },
                {
                    name: "负面",
                    type: "bar",
                    data: locationStats.locations.map(
                        (loc: string) =>
                            locationStats
                                .sentiment_by_location[
                                loc
                            ].negative
                    ),
                    itemStyle: {
                        color: "#f04141",
                    },
                },
            ],
        };
        locationBar.setOption(locationBarOption);
    }

    // 地域情感概率雷达图
    if (
        locationMapChart.value &&
        results.value.location_stats
    ) {
        const locationMap = echarts.init(
            locationMapChart.value
        );
        const locationStats =
            results.value.location_stats;

        // 选取前10个地区做雷达图
        const topLocations =
            locationStats.locations.slice(0, 10);

        const locationMapOption = {
            title: {
                text: "各地区平均情感概率对比",
                left: "center",
            },
            tooltip: {
                trigger: "item",
            },
            legend: {
                data: ["正面概率", "负面概率"],
                top: "10%",
            },
            radar: {
                indicator: topLocations.map(
                    (loc: string) => ({
                        name: loc,
                        max: 1,
                    })
                ),
                radius: "60%",
            },
            series: [
                {
                    type: "radar",
                    data: [
                        {
                            value: topLocations.map(
                                (loc: string) =>
                                    locationStats
                                        .avg_prob_by_location[
                                        loc
                                    ].positive
                            ),
                            name: "正面概率",
                            itemStyle: {
                                color: "#10dc60",
                            },
                            areaStyle: {
                                opacity: 0.3,
                            },
                        },
                        {
                            value: topLocations.map(
                                (loc: string) =>
                                    locationStats
                                        .avg_prob_by_location[
                                        loc
                                    ].negative
                            ),
                            name: "负面概率",
                            itemStyle: {
                                color: "#f04141",
                            },
                            areaStyle: {
                                opacity: 0.3,
                            },
                        },
                    ],
                },
            ],
        };
        locationMap.setOption(locationMapOption);
    }
};

const getSentimentColor = (
    sentiment: string
): string => {
    switch (sentiment) {
        case "positive":
            return "success";
        case "negative":
            return "danger";
        case "neutral":
            return "warning";
        default:
            return "medium";
    }
};

const getSentimentLabel = (
    sentiment: string
): string => {
    switch (sentiment) {
        case "positive":
            return "正面";
        case "negative":
            return "负面";
        case "neutral":
            return "中性";
        default:
            return "未知";
    }
};

const exportResults = () => {
    if (!results.value) return;

    // 创建CSV内容
    let csv =
        "评论,情感,正面概率,中性概率,负面概率\n";
    results.value.results.forEach((item: any) => {
        csv += `"${
            item.text
        }","${getSentimentLabel(
            item.sentiment
        )}",${item.probabilities.positive},${
            item.probabilities.neutral
        },${item.probabilities.negative}\n`;
    });

    // 下载文件
    const blob = new Blob(["\ufeff" + csv], {
        type: "text/csv;charset=utf-8;",
    });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `sentiment_analysis_${Date.now()}.csv`;
    link.click();

    showMessage("结果已导出", "success");
};

const showMessage = (
    message: string,
    color: string = "success"
) => {
    toastMessage.value = message;
    toastColor.value = color;
    showToast.value = true;
};

// 监听结果变化,重置分页
watch(
    () => results.value,
    () => {
        currentPage.value = 1;
    }
);
</script>

<style scoped>
.upload-section {
    margin-bottom: 20px;
}

.file-input {
    display: none;
}

.config-section {
    margin-top: 20px;
    margin-bottom: 20px;
}

.analyze-btn {
    margin-top: 20px;
}

.text-center {
    text-align: center;
    margin: 10px 0;
}

.statistics-grid {
    display: grid;
    grid-template-columns: repeat(
        auto-fit,
        minmax(120px, 1fr)
    );
    gap: 16px;
    margin-bottom: 24px;
}

.stat-item {
    text-align: center;
    padding: 16px;
    border-radius: 8px;
    background: var(--ion-color-light);
}

.stat-item.positive {
    background: rgba(16, 220, 96, 0.1);
}

.stat-item.neutral {
    background: rgba(255, 206, 0, 0.1);
}

.stat-item.negative {
    background: rgba(240, 65, 65, 0.1);
}

.stat-value {
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 8px;
}

.stat-label {
    font-size: 14px;
    color: var(--ion-color-medium);
}

.chart-container {
    width: 100%;
    height: 300px;
    margin: 20px 0;
}

.result-item h3 {
    font-size: 14px;
    margin: 8px 0;
    color: var(--ion-color-dark);
}

.sentiment-info {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 8px;
}

.probabilities {
    font-size: 12px;
    color: var(--ion-color-medium);
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
    margin-top: 16px;
}

.page-info {
    font-size: 14px;
    color: var(--ion-color-medium);
}

.chart-container-large {
    width: 100%;
    height: 400px;
    margin: 20px 0;
}

.category-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}

ion-item h3 {
    font-weight: 600;
    margin-bottom: 4px;
}

ion-item p {
    font-size: 14px;
    color: var(--ion-color-medium);
}
</style>
