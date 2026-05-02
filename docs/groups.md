# Tool catalog — 149 tools across 15 groups

Auto-generated from `tools/*/bd_*.py` by `scripts/generate_groups_doc.py`. Regenerate after any codegen run.

**Legend:** `smoke` = hand-written bootstrap tool (preserved across regen). `write` = mutating op, gated by `BD_ENABLE_WRITES=true`.

## Summary

| Group | Tools |
|---|---:|
| [`account_management`](#account_management) | 70 |
| [`archive`](#archive) | 6 |
| [`browser_api`](#browser_api) | 2 |
| [`deep_lookup`](#deep_lookup) | 9 |
| [`marketplace_dataset`](#marketplace_dataset) | 25 |
| [`misc`](#misc) | 6 |
| [`proxy`](#proxy) | 3 |
| [`proxy_manager`](#proxy_manager) | 1 |
| [`rest_api`](#rest_api) | 0 |
| [`scraper_studio`](#scraper_studio) | 13 |
| [`scrapers`](#scrapers) | 3 |
| [`scraping_shield`](#scraping_shield) | 4 |
| [`serp`](#serp) | 3 |
| [`unlocker_rest`](#unlocker_rest) | 3 |
| [`video_downloader`](#video_downloader) | 1 |
| **Total** | **149** |

## account_management

_70 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_account_get_balance` | get the total Bright Data account balance. | smoke |
| `bd_account_get_status` | get the Bright Data account status. | smoke |
| `bd_account_management_create_api_by_partner_name_signup_dedicated_dc` | auto-generated tool for POST /api/{PARTNER_NAME}/signup_dedicated_dc. | write |
| `bd_account_management_create_api_by_partner_name_signup_dedicated_isp` | auto-generated tool for POST /api/{PARTNER_NAME}/signup_dedicated_isp. | write |
| `bd_account_management_create_api_by_partner_name_signup_residential` | auto-generated tool for POST /api/{PARTNER_NAME}/signup_residential. | write |
| `bd_account_management_create_api_by_partner_name_signup_shared_dc` | auto-generated tool for POST /api/{PARTNER_NAME}/signup_shared_dc. | write |
| `bd_account_management_create_api_by_partner_name_signup_shared_isp` | auto-generated tool for POST /api/{PARTNER_NAME}/signup_shared_isp. | write |
| `bd_account_management_create_api_by_partner_name_signup_smart_resi` | auto-generated tool for POST /api/{PARTNER_NAME}/signup_smart_resi. | write |
| `bd_account_management_create_api_by_partner_name_usage_webhook` | auto-generated tool for POST /api/{PARTNER_NAME}/usage_webhook. | write |
| `bd_account_management_create_zone` | auto-generated tool for POST /zone. | write |
| `bd_account_management_create_zone_add_password` | auto-generated tool for POST /zone/add_password. | write |
| `bd_account_management_create_zone_blacklist` | auto-generated tool for POST /zone/blacklist. | write |
| `bd_account_management_create_zone_change_disable` | auto-generated tool for POST /zone/change_disable. | write |
| `bd_account_management_create_zone_domain_perm` | auto-generated tool for POST /zone/domain_perm. | write |
| `bd_account_management_create_zone_ips` | auto-generated tool for POST /zone/ips. | write |
| `bd_account_management_create_zone_ips_migrate` | auto-generated tool for POST /zone/ips/migrate. | write |
| `bd_account_management_create_zone_ips_refresh` | auto-generated tool for POST /zone/ips/refresh. | write |
| `bd_account_management_create_zone_remove_password` | auto-generated tool for POST /zone/remove_password. | write |
| `bd_account_management_create_zone_switch_100uptime` | auto-generated tool for POST /zone/switch_100uptime. | write |
| `bd_account_management_create_zone_whitelist` | auto-generated tool for POST /zone/whitelist. | write |
| `bd_account_management_delete_api_by_partner_name_ips` | auto-generated tool for DELETE /api/{PARTNER_NAME}/ips. | write |
| `bd_account_management_delete_zone` | auto-generated tool for DELETE /zone. | write |
| `bd_account_management_delete_zone_blacklist` | auto-generated tool for DELETE /zone/blacklist. | write |
| `bd_account_management_delete_zone_domain_perm` | auto-generated tool for DELETE /zone/domain_perm. | write |
| `bd_account_management_delete_zone_ips` | auto-generated tool for DELETE /zone/ips. | write |
| `bd_account_management_delete_zone_vips` | auto-generated tool for DELETE /zone/vips. | write |
| `bd_account_management_delete_zone_whitelist` | auto-generated tool for DELETE /zone/whitelist. | write |
| `bd_account_management_get_api_by_partner_name_carrier_ips_count` | auto-generated tool for GET /api/{PARTNER_NAME}/carrier_ips_count. | — |
| `bd_account_management_get_api_by_partner_name_carriers` | auto-generated tool for GET /api/{PARTNER_NAME}/carriers. | — |
| `bd_account_management_get_api_by_partner_name_countries` | auto-generated tool for GET /api/{PARTNER_NAME}/countries. | — |
| `bd_account_management_get_api_by_partner_name_customers` | auto-generated tool for GET /api/{PARTNER_NAME}/customers. | — |
| `bd_account_management_get_api_by_partner_name_get_asn` | auto-generated tool for GET /api/{PARTNER_NAME}/get_asn. | — |
| `bd_account_management_get_api_by_partner_name_ips` | auto-generated tool for GET /api/{PARTNER_NAME}/ips. | — |
| `bd_account_management_get_api_by_partner_name_proxies` | auto-generated tool for GET /api/{PARTNER_NAME}/proxies. | — |
| `bd_account_management_get_api_by_partner_name_shared_isp` | auto-generated tool for GET /api/{PARTNER_NAME}/shared_isp. | — |
| `bd_account_management_get_api_by_partner_name_socks5_proxies` | auto-generated tool for GET /api/{PARTNER_NAME}/socks5_proxies. | — |
| `bd_account_management_get_api_by_partner_name_usage_limit` | auto-generated tool for GET /api/{PARTNER_NAME}/usage_limit. | — |
| `bd_account_management_get_api_by_partner_name_usage_limit_stats` | auto-generated tool for GET /api/{PARTNER_NAME}/usage_limit_stats. | — |
| `bd_account_management_get_api_by_partner_name_usage_webhook` | auto-generated tool for GET /api/{PARTNER_NAME}/usage_webhook. | — |
| `bd_account_management_get_customer_balance` | auto-generated tool for GET /customer/balance. | — |
| `bd_account_management_get_customer_bw` | auto-generated tool for GET /customer/bw. | — |
| `bd_account_management_get_network_status_by_network_type` | auto-generated tool for GET /network_status/{NETWORK_TYPE}. | — |
| `bd_account_management_get_zone` | auto-generated tool for GET /zone. | — |
| `bd_account_management_get_zone_blacklist` | auto-generated tool for GET /zone/blacklist. | — |
| `bd_account_management_get_zone_bw` | auto-generated tool for GET /zone/bw. | — |
| `bd_account_management_get_zone_cost` | auto-generated tool for GET /zone/cost. | — |
| `bd_account_management_get_zone_ips_unavailable` | auto-generated tool for GET /zone/ips/unavailable. | — |
| `bd_account_management_get_zone_proxies_pending_replacement` | auto-generated tool for GET /zone/proxies_pending_replacement. | — |
| `bd_account_management_get_zone_whitelist` | auto-generated tool for GET /zone/whitelist. | — |
| `bd_account_management_list_all_available_countries_per_zone_type` | auto-generated tool for GET /countrieslist. | — |
| `bd_account_management_list_cities` | auto-generated tool for GET /cities. | — |
| `bd_account_management_list_status` | auto-generated tool for GET /status. | — |
| `bd_account_management_list_zone_count_available_ips` | auto-generated tool for GET /zone/count_available_ips. | — |
| `bd_account_management_list_zone_get_active_zones` | auto-generated tool for GET /zone/get_active_zones. | — |
| `bd_account_management_list_zone_get_all_zones` | auto-generated tool for GET /zone/get_all_zones. | — |
| `bd_account_management_list_zone_ips` | auto-generated tool for GET /zone/ips. | — |
| `bd_account_management_list_zone_passwords` | auto-generated tool for GET /zone/passwords. | — |
| `bd_account_management_list_zone_permissions` | auto-generated tool for GET /zone/permissions. | — |
| `bd_account_management_list_zone_recent_ips` | auto-generated tool for GET /zone/recent_ips. | — |
| `bd_account_management_list_zone_route_ips` | auto-generated tool for GET /zone/route_ips. | — |
| `bd_account_management_list_zone_route_vips` | auto-generated tool for GET /zone/route_vips. | — |
| `bd_account_management_list_zone_static_cities` | auto-generated tool for GET /zone/static/cities. | — |
| `bd_account_management_list_zone_status` | auto-generated tool for GET /zone/status. | — |
| `bd_account_management_update_api_by_partner_name_disable_customer` | auto-generated tool for PUT /api/{PARTNER_NAME}/disable_customer. | write |
| `bd_account_management_update_api_by_partner_name_enable_customer` | auto-generated tool for PUT /api/{PARTNER_NAME}/enable_customer. | write |
| `bd_account_management_update_api_by_partner_name_ips` | auto-generated tool for PUT /api/{PARTNER_NAME}/ips. | write |
| `bd_account_management_update_api_by_partner_name_refresh_ips` | auto-generated tool for PUT /api/{PARTNER_NAME}/refresh_ips. | write |
| `bd_account_management_update_api_by_partner_name_usage_limit` | auto-generated tool for PUT /api/{PARTNER_NAME}/usage_limit. | write |
| `bd_account_management_update_status` | auto-generated tool for PUT /status. | write |
| `bd_zones_list` | list active zones in the Bright Data account. | smoke |

## archive

_6 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_archive_create_webarchive_dump` | auto-generated tool for POST /webarchive/dump. | write |
| `bd_archive_create_webarchive_search` | auto-generated tool for POST /webarchive/search. | write |
| `bd_archive_get_webarchive_dump_by_dump_id` | auto-generated tool for GET /webarchive/dump/{dump_id}. | — |
| `bd_archive_get_webarchive_search_by_search_id` | auto-generated tool for GET /webarchive/search/{search_id}. | — |
| `bd_archive_list_webarchive_dumps` | auto-generated tool for GET /webarchive/dumps. | — |
| `bd_archive_list_webarchive_searches` | auto-generated tool for GET /webarchive/searches. | — |

## browser_api

_2 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_browser_api_get_browser_sessions_by_session_id` | auto-generated tool for GET /browser_sessions/{session_id}. | — |
| `bd_browser_api_list_browser_sessions` | auto-generated tool for GET /browser_sessions. | — |

## deep_lookup

_9 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_deep_lookup_create_enhance_query` | auto-generated tool for POST /enhance_query. | write |
| `bd_deep_lookup_create_preview` | auto-generated tool for POST /preview. | write |
| `bd_deep_lookup_create_request_by_id_cancel` | auto-generated tool for POST /request/{id}/cancel. | write |
| `bd_deep_lookup_create_request_by_id_enrich` | auto-generated tool for POST /request/{id}/enrich. | write |
| `bd_deep_lookup_create_trigger` | auto-generated tool for POST /trigger. | write |
| `bd_deep_lookup_get_preview_by_id` | auto-generated tool for GET /preview/{id}. | — |
| `bd_deep_lookup_get_request_by_id` | auto-generated tool for GET /request/{id}. | — |
| `bd_deep_lookup_get_request_by_id_download` | auto-generated tool for GET /request/{id}/download. | — |
| `bd_deep_lookup_get_request_by_id_status` | auto-generated tool for GET /request/{id}/status. | — |

## marketplace_dataset

_25 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_marketplace_dataset_create_datasets_filter` | auto-generated tool for POST /datasets/filter. | write |
| `bd_marketplace_dataset_create_datasets_snapshots_by_id_deliver` | auto-generated tool for POST /datasets/snapshots/{id}/deliver. | write |
| `bd_marketplace_dataset_create_datasets_v3_deliver_by_snapshot_id` | auto-generated tool for POST /datasets/v3/deliver/{snapshot_id}. | write |
| `bd_marketplace_dataset_create_datasets_v3_scrape` | auto-generated tool for POST /datasets/v3/scrape. | write |
| `bd_marketplace_dataset_create_datasets_v3_snapshot_by_snapshot_id_cancel` | auto-generated tool for POST /datasets/v3/snapshot/{snapshot_id}/cancel. | write |
| `bd_marketplace_dataset_create_datasets_v3_snapshot_by_snapshot_id_rerun` | auto-generated tool for POST /datasets/v3/snapshot/{snapshot_id}/rerun. | write |
| `bd_marketplace_dataset_create_datasets_v3_trigger` | auto-generated tool for POST /datasets/v3/trigger. | write |
| `bd_marketplace_dataset_get_datasets_delivery_settings_by_destination_type_schema` | auto-generated tool for GET /datasets/delivery_settings/{destination_type}/schema. | — |
| `bd_marketplace_dataset_get_datasets_snapshots_by_id` | auto-generated tool for GET /datasets/snapshots/{id}. | — |
| `bd_marketplace_dataset_get_datasets_snapshots_by_id_download` | auto-generated tool for GET /datasets/snapshots/{id}/download. | — |
| `bd_marketplace_dataset_get_datasets_snapshots_by_id_parts` | auto-generated tool for GET /datasets/snapshots/{id}/parts. | — |
| `bd_marketplace_dataset_get_datasets_v3_delivery_by_delivery_id` | auto-generated tool for GET /datasets/v3/delivery/{delivery_id}. | — |
| `bd_marketplace_dataset_get_datasets_v3_log_by_snapshot_id` | auto-generated tool for GET /datasets/v3/log/{snapshot_id}. | — |
| `bd_marketplace_dataset_get_datasets_v3_progress_by_snapshot_id` | auto-generated tool for GET /datasets/v3/progress/{snapshot_id}. | — |
| `bd_marketplace_dataset_get_datasets_v3_snapshot_by_snapshot_id` | auto-generated tool for GET /datasets/v3/snapshot/{snapshot_id}. | — |
| `bd_marketplace_dataset_get_datasets_v3_snapshot_by_snapshot_id_input` | auto-generated tool for GET /datasets/v3/snapshot/{snapshot_id}/input. | — |
| `bd_marketplace_dataset_get_datasets_v3_snapshot_by_snapshot_id_parts` | auto-generated tool for GET /datasets/v3/snapshot/{snapshot_id}/parts. | — |
| `bd_marketplace_dataset_get_datasets_views_by_view_id_delivery_settings` | auto-generated tool for GET /datasets/views/{view_id}/delivery_settings. | — |
| `bd_marketplace_dataset_list_datasets` | auto-generated tool for GET /datasets/list. | — |
| `bd_marketplace_dataset_list_datasets_delivery_settings_options` | auto-generated tool for GET /datasets/delivery_settings/options. | — |
| `bd_marketplace_dataset_list_datasets_snapshots` | auto-generated tool for GET /datasets/snapshots. | — |
| `bd_marketplace_dataset_list_datasets_v3_snapshots` | auto-generated tool for GET /datasets/v3/snapshots. | — |
| `bd_marketplace_dataset_list_datasets_views` | auto-generated tool for GET /datasets/views. | — |
| `bd_marketplace_dataset_update_datasets_views_by_view_id_delivery_settings` | auto-generated tool for PUT /datasets/views/{view_id}/delivery_settings. | write |
| `bd_marketplace_dataset_update_datasets_views_delivery_settings_bulk` | auto-generated tool for PUT /datasets/views/delivery_settings/bulk. | write |

## misc

_6 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_misc_create_datasets_filter` | auto-generated tool for POST /datasets/filter. | write |
| `bd_misc_create_datasets_v3_scrape` | auto-generated tool for POST /datasets/v3/scrape. | write |
| `bd_misc_create_serp_req` | auto-generated tool for POST /serp/req. | write |
| `bd_misc_create_unblocker_req` | auto-generated tool for POST /unblocker/req. | write |
| `bd_misc_get_serp_get_result` | auto-generated tool for GET /serp/get_result. | — |
| `bd_misc_get_unblocker_get_result` | auto-generated tool for GET /unblocker/get_result. | — |

## proxy

_3 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_proxy_create_request` | auto-generated tool for POST /request. | write |
| `bd_proxy_get_request` | auto-generated tool for GET /request. | — |
| `bd_proxy_get_response` | auto-generated tool for GET /response. | — |

## proxy_manager

_1 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_proxy_manager_get_domain_metrics` | auto-generated tool for GET /domains/{metric}. | — |

## rest_api

_0 tools._

(no tools — group reserved for future endpoints)

## scraper_studio

_13 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_scraper_studio_create_dca_collector` | auto-generated tool for POST /dca/collector. | write |
| `bd_scraper_studio_create_dca_collectors_by_collector_id_automate_template` | auto-generated tool for POST /dca/collectors/{collector_id}/automate_template. | write |
| `bd_scraper_studio_create_dca_collectors_by_collector_id_refactor_template` | auto-generated tool for POST /dca/collectors/{collector_id}/refactor_template. | write |
| `bd_scraper_studio_create_dca_crawl` | auto-generated tool for POST /dca/crawl. | write |
| `bd_scraper_studio_create_dca_trigger` | auto-generated tool for POST /dca/trigger. | write |
| `bd_scraper_studio_create_dca_trigger_hp` | auto-generated tool for POST /dca/trigger_hp. | write |
| `bd_scraper_studio_create_dca_trigger_immediate` | auto-generated tool for POST /dca/trigger_immediate. | write |
| `bd_scraper_studio_get_dca_collectors_by_collector_id_automate_template_progress` | auto-generated tool for GET /dca/collectors/{collector_id}/automate_template/progress. | — |
| `bd_scraper_studio_get_dca_collectors_by_collector_id_refactor_template_progress` | auto-generated tool for GET /dca/collectors/{collector_id}/refactor_template/progress. | — |
| `bd_scraper_studio_get_dca_dataset` | auto-generated tool for GET /dca/dataset. | — |
| `bd_scraper_studio_get_dca_get_result` | auto-generated tool for GET /dca/get_result. | — |
| `bd_scraper_studio_get_dca_jobs_by_job_id_hp_errors` | auto-generated tool for GET /dca/jobs/{job_id}/hp_errors. | — |
| `bd_scraper_studio_get_dca_log_by_job_id` | auto-generated tool for GET /dca/log/{job_id}. | — |

## scrapers

_3 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_scrapers_create_datasets_v3_trigger` | auto-generated tool for POST /datasets/v3/trigger. | write |
| `bd_scrapers_get_datasets_v3_progress_by_snapshot_id` | auto-generated tool for GET /datasets/v3/progress/{snapshot_id}. | — |
| `bd_scrapers_get_datasets_v3_snapshot_by_snapshot_id` | auto-generated tool for GET /datasets/v3/snapshot/{snapshot_id}. | — |

## scraping_shield

_4 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_scraping_shield_get_shield_domains_by_class` | auto-generated tool for GET /shield/domains_by_class. | — |
| `bd_scraping_shield_get_shield_zones_by_class` | auto-generated tool for GET /shield/zones_by_class. | — |
| `bd_scraping_shield_list_shield_class` | auto-generated tool for GET /shield/class. | — |
| `bd_scraping_shield_list_shield_samples` | auto-generated tool for GET /shield/samples. | — |

## serp

_3 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_serp_create_request` | auto-generated tool for POST /request. | write |
| `bd_serp_get_request` | auto-generated tool for GET /request. | — |
| `bd_serp_get_response` | auto-generated tool for GET /response. | — |

## unlocker_rest

_3 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_unlocker_rest_create_request` | auto-generated tool for POST /request. | write |
| `bd_unlocker_rest_get_request` | auto-generated tool for GET /request. | — |
| `bd_unlocker_rest_get_response` | auto-generated tool for GET /response. | — |

## video_downloader

_1 tools._

| Tool | Description | Flags |
|---|---|---|
| `bd_video_downloader_trigger_video_download` | auto-generated tool for POST /dca/trigger_hp. | write |

