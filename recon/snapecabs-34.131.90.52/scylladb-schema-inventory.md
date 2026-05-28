# ScyllaDB Alternator Schema Inventory
**Target:** 34.131.90.52  
**Date:** 2026-05-28  
**Method:** ScyllaDB REST API (port 10000) + CQL native (port 9042, cassandra/cassandra)

---

## Cluster Topology

| Field | Value |
|-------|-------|
| Cluster name | Test Cluster |
| ScyllaDB version | 3.0.8 |
| Node count | 2 |
| Nodes | 10.190.0.4 (local), 10.190.0.11 (peer) |
| DC/Rack | datacenter1 / rack1 |
| CQL auth | PasswordAuthenticator (cassandra/cassandra) |
| DynamoDB port 8000 | Auth required (UnrecognizedClientException on unknown user) |
| REST API port 10000 | Open, no auth |

---

## Keyspace Count

**Total keyspaces:** 108 (non-system: ~100 alternator_ keyspaces)

---

## High-Value Table Inventory

### Authentication / Session Layer

**alternator_auth_tokens.auth_tokens** -- 245 rows  
PK: userId + sessionKey  
Attributes: `authToken`, `createDate`, `createdDateTime`, `createdEpochTime`, `expiryTime`, `id`, `lastAccessed`, `refreshToken`, `refreshTokenValidity`, `valid`  
CDC log active. Full session token material: bearer tokens + refresh tokens + expiry + validity flags.

**alternator_user_accounts.user_accounts** -- 0 rows (likely prod-empty test instance)  
PK: user_id  
Indexed by: customer_id, parentId, vehicleGroup, vehicleId

**alternator_manage-session.manage-session**  
PK: vendorName (vendor-namespaced sessions)

**alternator_firebase_device_token.firebase_device_token** -- 0 rows  
PK: userId + deviceToken  
Push notification credentials.

---

### Driver / Personnel Data

**alternator_driver-data.driver-data** -- 0 rows  
PK: customer_id + timeDriverId  
Indexed by: fleet_manager_id, novusfleet_userid  
Attributes: stored in `:attrs` blob (schema-on-write DynamoDB model)

**alternator_driver-vehicle-mapping.driver-vehicle-mapping**  
PK: customerId + driverVehicleSortKey  
Indexed by: driverId, deviceId, vehicleId  
Links driver identity to vehicle/device assignments.

**alternator_driver-performance.driver-performance** -- 0 rows  
PK: driverId + date_time  
Indexed by: fleetId, vehicleGroup, fleetAdminId

**alternator_driver-coaching.driver-coaching**  
PK+indexes: fleetAdminId, fleetId  
Coaching session records per driver.

**alternator_driver-coaching-broadcast-schedule.driver-coaching-broadcast-schedule**  
Scheduled coaching broadcast records.

---

### Vehicle Telemetry / IoT

**alternator_vehicle-current-state.vehicle-current-state** -- 6 rows  
PK: vehicleId  
Attributes: `companyCode`, `country`, `createdAt`, `dateTimeInMillisecons`, `deviceId`, `deviceType`, `deviceWakeupTriggered`, `fleetId`, `fuelDeviceId`, `gpsSpeed`, `groupName`, `hasDevice`, `lastLatitude`, `lastLongitude`, `lastUpdateTime`, `parentId`, `timeZone`, `totalKmToday`, `vehicleState`, `vehicleType`  
Real-time GPS lat/long + speed per vehicle.

**alternator_IotData.IotData** -- 1 row  
PK: device_id + timestamp  
CDC log active. Raw IoT device telemetry stream.

**alternator_fcw-iot-device.fcw-iot-device** -- 5 rows  
PK: vehicleId  
Attributes (60+ fields): `activeTime`, `blurStatus`, `camCount`, `cameraBlockStatus`, `cameraMalFunctionStatus`, `companyCode`, `country`, `customerId`, `dataSource`, `deviceId`, `deviceType`, `dmsCameraStatus`, `dsmCameraPosition`, `errorStatus`, `fcwCameraStatus`, `fovStatus`, `gpsSpeed`, `gpsStatus`, `groupName`, `ignitionStatus`, `imuStatus`, `inCabinCameraStatus`, `lastAlarmCode`, `lastAlarmDataTime`, `lastLatitude`, `lastLongitude`, `lowVisibilityStatus`, `maxLiveStreamViewers`, `micStatus`, `onlineState`, `parent_id`, `powerTamperingStatus`, `rearCameraStatus`, `sdCardStatus`, `signalStrengthStatus`, `sosStatus`, `speakerStatus`, `totalKmToday`, `totalUsedMb`, `tripStatus`, `vehicleState`, `vehicleType`, `version`  
FCW (Forward Collision Warning) device registry with full sensor state.

**alternator_fcw_device_current_status.fcw_device_current_status** -- 58 rows  
PK: deviceId + date_time  
Real-time FCW device status log.

**alternator_adas_all_device_current_status_replica.adas_all_device_current_status_replica** -- 30 rows  
ADAS (Advanced Driver Assistance Systems) device replica status.  
Indexed by: vehicleGroup, parentId, fleetId + date_time.

**alternator_fcw_ignition_data.fcw_ignition_data**  
PK: device_id + warningSortKey  
Ignition on/off events per device.

**alternator_emqx-device-activity.emqx-device-activity** -- 127 rows  
PK: deviceId + transactionId  
EMQX MQTT broker device activity log.

---

### Warning / Safety Events

**alternator_fcw-warnings.fcw-warnings** -- 431,808 rows  
PK: device_id + warningSortKey  
CDC log active.  
Attributes: `customer_id`, `dataCreatedTime`, `date_time`, `deviceType`, `driverId`, `driverName`, `driverWarningType`, `gpsLat`, `gpsLong`, `gpsSpeed`, `ignitionState`, `overspeed_duration`, `signalLevel`, `trip_duration`, `vehicleId`, `warningStatus`  
Most populated table. Contains driverName + GPS coordinates per warning event.

**alternator_actual_warning.actual_warning** -- 1,236 rows  
PK: device_id + warningSortKey  
Attributes: `alert_id`, `driverId`, `driverName`, `driverWarningType`, `faceRoi`, `fleet_id`, `gpsLat`, `gpsLong`, `gpsSpeed`, `parent_id`, `tripId`, `vehicleId`, `vehicle_group`, `videoFileName`, `warningStatus`  
Includes `faceRoi` (face region-of-interest from in-cabin camera) and `videoFileName` (S3 key reference).

**alternator_health_report.health_report** -- 78 rows  
PK: device_id + warningSortKey

**alternator_adas_linux_device_messages.adas_linux_device_messages**  
PK: deviceId + warningSortKey

**alternator_assigned-critical-non-critical-warning.assigned-critical-non-critical-warning**  
PK + parentId index. Warning triage/assignment table.

---

### Trip / Ride Data

**alternator_trip-info.trip-info** -- 0 rows  
PK: fleetManagerId + tripId  
Indexed by: deviceId, fleetAdminId, groupName

**alternator_snapecabs-ride-logs.snapecabs-ride-logs** -- 0 rows  
PK: deviceId + timeStamp  
Indexed by: fleetAdminId, fleetManagerId + timeStamp  
SnapeCabs (ride-hailing) specific ride log table.

**alternator_mahindra-trip-payloads.mahindra-trip-payloads** -- 0 rows  
PK: companyName + trip-payloads  
Mahindra OEM trip payload integration.

---

### Video / Streaming

**alternator_footage_video_file.footage_video_file**  
PK indexes: requestId, fleetAdminId, createdDateTime, fleetManagerId, tripId  
Video footage file records (S3 references).

**alternator_video-demand-request.video-demand-request** / **v2**  
Video on demand request records, indexed by tripId, fleetAdminId, deviceId, vehicleId.

**alternator_video_streams_and_channels.video_streams_and_channels**  
PK: deviceId + createdAt index  
Live stream channel registry.

**alternator_vod-file-upload.vod-file-upload**  
Video file upload tracking.

**alternator_android-livestream.android-livestream** / **alternator_android-playback.android-playback**  
Mobile client streaming session records.

**alternator_vp2-playback.vp2-playback** / **alternator_vp2-streaming-url.vp2-streaming-url** / **alternator_vp2_device_data.vp2_device_data**  
VP2 (dashcam hardware generation) playback and streaming records.

**alternator_live-stream-vp2.live-stream-vp2** / **alternator_live-stream-stop.live-stream-stop**  
Live stream session lifecycle.

**alternator_sdcard_playback_request.sdcard_playback_request** / **alternator_download-sd-card-vp2.download-sd-card-vp2** / **alternator_upload-download-sd-card-vp2.upload-download-sd-card-vp2**  
SD card content retrieval pipeline (on-device to cloud).

---

### Fleet / Org Management

**alternator_device_list.device_list** -- 1 row  
Master device registry.

**alternator_device_certificates.device_certificates**  
Device TLS/auth certificate store.

**alternator_groups.groups**  
PK + indexed by parentId, groupName. Fleet group hierarchy.

**alternator_vehicle_groups.vehicle_groups**  
Vehicle group assignments.

**alternator_geofence.geofence** -- 2 rows  
PK: geofenceCode. Indexed by fleetAdminId, customerId.

**alternator_address_book.address_book**  
Indexed by customerId, fleetAdminId.

**alternator_route-info.route-info** / **alternator_route-path.route-path**  
Route definitions and path coordinates.

**alternator_fleet_document_reminder.fleet_document_reminder**  
Document expiry tracking.

**alternator_fleets_docments.fleets_docments**  
Fleet document storage (insurance, registration, etc). Multiple indexes including expiryStatus and documentUniqueId.

**alternator_fleet-safety-guidelines.fleet-safety-guidelines**  
Safety policy configuration per fleet.

**alternator_fleet-daily-summary.fleet-daily-summary**  
Daily summary aggregates per fleetAdmin + date_time.

---

### ML / AI Configuration

**alternator_ml-config.ml-config**  
PK: productType  
Indexed by: productType + latestConfig  
Attributes: `config`, `latestConfig`, `mlConfigCreatedAt`, `transactionId`, `updatedBy`, `updatedSource`  
productType values observed: numeric IMEI strings (863386074024828, 863386074033936) and "CAB"  
Per-device ML model configuration with version tracking.

**alternator_ml-config-device-request.ml-config-device-request**  
Indexed by: deviceId + configStatus  
ML config push request queue to individual devices.

**alternator_gen-config.gen-config** / **alternator_gen-config-device-request.gen-config-device-request**  
General firmware/config distribution pipeline.

---

### Notifications / Comms

**alternator_omnifleet-notification.omnifleet-notification**  
PK + fleetAdminId + date_time index. Push notification records.

**alternator_broadcast.broadcast** -- 1 row  
PK: broadcastId + dateTime  
Indexed by fleetId, fleetAdminId, nextTriggerTimeDue.

**alternator_firebase_device_token.firebase_device_token** -- 0 rows  
PK: userId + deviceToken

---

### Subscription / Billing

**alternator_channel-subscription.channel-subscription**  
Indexed by fleetAdminId, superAdminId + subscriptionSortKey.

**alternator_internal-subscription.internal-subscription**  
Indexed by deviceId.

**alternator_fleetgpt_subscription.fleetgpt_subscription** -- 0 rows  
PK: customerId. FleetGPT AI assistant subscription tier.

**alternator_daily_consumed_data.daily_consumed_data**  
Data consumption metering by fleet, vehicleGroup, parentId + date_time.

---

### Support

**alternator_support_helpdesk_ticket.support_helpdesk_ticket** -- 5 rows  
PK: fleetId + ticketId  
Attributes: `category`, `createdDate`, `createdTime`, `deletedMediaS3Keys`, `mediaS3Keys`, `mediaUrls`, `message`, `organizationName`, `priority`, `raisedBy`, `reply`, `status`, `statusHistory`, `superAdminId`, `vehicleId`  
Full helpdesk ticket content including message text, org name, S3 media keys.

---

### Misc / Operational

**alternator_api_rate_limit.api_rate_limit** -- rate limiting state  
**alternator_manage-alerts.manage-alerts** -- alert configuration  
**alternator_manage-session.manage-session** -- session management by vendorName  
**alternator_comments_history.comments_history** -- warning review comments  
**alternator_delete-history-user.delete-history-user** -- soft-delete audit log  
**alternator_device-delete-stuff.device-delete-stuff** -- device decommission records  
**alternator_reverse_geocode_api_count.reverse_geocode_api_count** -- geocoding API usage  
**alternator_google-geo-address.google-geo-address** -- geocoded address cache  
**alternator_report_master.report_master** -- report template registry  
**alternator_custom_report_template.custom_report_template** -- custom reports  
**alternator_scheduled_reports.scheduled_reports** -- scheduled report queue  
**alternator_passenger-occupancy-report.passenger-occupancy-report** -- occupancy analytics  
**alternator_speed-based-occupancy.speed-based-occupancy** -- speed-correlated occupancy  
**alternator_banner-info.banner-info** -- UI banner configuration  
**alternator_app-menu-novus.app-menu-novus** -- app menu configuration  
**alternator_user-permission-menu-access.user-permission-menu-access** -- RBAC menu ACLs  
**alternator_user_banner_dismissals.user_banner_dismissals** -- UI state  
**alternator_alert_config_cloud.alert_config_cloud** -- cloud alert thresholds  
**alternator_invalid_alarm_config_request.invalid_alarm_config_request** -- config error log  
**alternator_fleet-feature.fleet-feature** -- feature flags by fleet  
**alternator_fleet_live_stream_config.fleet_live_stream_config** -- streaming config per fleet  
**alternator_live_stream_settings.live_stream_settings** -- stream quality settings  
**alternator_machine-config-params.machine-config-params** -- hardware config params  
**alternator_mqtt_non_warning.mqtt_non_warning** -- non-warning MQTT events  
**alternator_emqx-commands-logs.emqx-commands-logs** -- MQTT command history  
**alternator_emqx-device-config-ack.emqx-device-config-ack** -- config push ACKs  
**alternator_emqx-device-ota.emqx-device-ota** -- OTA update state  
**alternator_emqx-os-upload.emqx-os-upload** -- OS firmware uploads  
**alternator_emqx-apk-upload-data.emqx-apk-upload-data** -- APK deployment records  
**alternator_apk-upload-data.apk-upload-data** -- APK artifact metadata  
**alternator_device-ota-update.device-ota-update** -- OTA job tracking  
**alternator_device-status.device-status** -- device health state  
**alternator_device-streaming.device-streaming** -- active stream sessions  
**alternator_device-logs.device-logs** / **alternator_device-logs-emqx.device-logs-emqx** -- device log files  
**alternator_stop-streaming-vp2-device.stop-streaming-vp2-device** -- stream termination records  
**alternator_ignition-status-track-driver.ignition-status-track-driver** -- ignition event / driver tracking  
**alternator_fcw-iot-device-health.fcw-iot-device-health** -- FCW device health events  
**alternator_driver-event-track-coaching.driver-event-track-coaching** -- event-triggered coaching  
**alternator_driver-fetch-from-device.driver-fetch-from-device** -- driver data sync records  
**alternator_driver-unauthorized-fetch-for-video.driver-unauthorized-fetch-for-video** -- unauthorized video access attempts  
**alternator_fcw_device_current_status_replica.fcw_device_current_status_replica** -- replica of FCW status  
**alternator_adas_all_device_current_status_replica.adas_all_device_current_status_replica** -- ADAS replica status  
**alternator_geofence-enable-disable-recording.geofence-enable-disable-recording** -- geofence audit log  
**alternator_geofence-record-disable-enable.geofence-record-disable-enable** -- geofence state changes  
**alternator_general-params-setting.general-params-setting** -- fleet general settings  

---

## Data Classes Confirmed by Schema

| Class | Tables | Sensitivity |
|-------|--------|-------------|
| Authentication tokens (bearer + refresh) | auth_tokens | CRITICAL |
| Driver PII (name, driverId, face ROI) | fcw-warnings, actual_warning, driver-data | HIGH |
| Real-time GPS (lat/long, speed per vehicle) | vehicle-current-state, fcw-iot-device, fcw-warnings, actual_warning | HIGH |
| In-cabin video references (S3 keys) | actual_warning (videoFileName), footage_video_file, vod-file-upload | HIGH |
| Device/fleet operational state | 30+ tables | MEDIUM |
| ML model config (per device IMEI) | ml-config, ml-config-device-request | MEDIUM |
| Support ticket content + org names | support_helpdesk_ticket | MEDIUM |
| OTA firmware + APK distribution | emqx-device-ota, device-ota-update, apk-upload-data | MEDIUM |
| Firebase push tokens | firebase_device_token | MEDIUM |
| Ride-hailing logs (SnapeCabs) | snapecabs-ride-logs | MEDIUM |
| Mahindra OEM trip payloads | mahindra-trip-payloads | MEDIUM |

---

## Attack Surface Summary

1. **auth_tokens (245 rows, REST open):** Full bearer + refresh token material exposed. ScyllaDB REST API (port 10000) has no authentication. DynamoDB API (port 8000) requires auth but CQL (9042) accepts cassandra/cassandra defaults.

2. **fcw-warnings (431,808 rows):** Largest table. driverName + GPS coordinates + warning type per event. CDC log active means change stream accessible.

3. **actual_warning (1,236 rows):** Includes faceRoi (biometric inference data) and videoFileName (S3 path to in-cabin footage).

4. **vehicle-current-state + fcw-iot-device:** Real-time fleet GPS and 60+ sensor state fields per vehicle including SOS status, power tampering, in-cabin camera status.

5. **support_helpdesk_ticket (5 rows):** Free-text message content, organization names, S3 media URLs.

6. **IotData + emqx tables:** Raw MQTT telemetry with CDC active on IotData.

7. **cassandra/cassandra default credentials:** CQL port 9042 accessible with factory defaults -- full read/write access to all keyspaces.
