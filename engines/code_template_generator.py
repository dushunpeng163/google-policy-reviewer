"""
代码模板生成引擎

根据 App 的功能特性和目标平台，生成合规所需的具体实现代码：
- iOS (Swift)
- Android (Kotlin)
- Unity (C#)  — 跨平台，底层调用 StoreKit / Play Billing

使用方式：
  from engines.code_template_generator import generate_templates
  templates = generate_templates(features=['iap', 'att', 'kids'], platforms=['ios', 'android', 'unity'])
"""

from typing import List, Dict, Any

# ── 模板库 ───────────────────────────────────────────────────────────────────

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IAP / 应用内购买
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMPLATE_IAP_SWIFT = '''// ── IAP Manager (StoreKit 2) ──────────────────────────────────────
// 合规要点：所有虚拟商品必须通过 StoreKit，不得引导外部支付
// 参考：App Store Guideline 3.1.1

import StoreKit

enum StoreError: Error { case failedVerification }

@MainActor
class IAPManager: ObservableObject {
    static let shared = IAPManager()

    @Published var products: [Product] = []
    @Published var purchasedProductIDs: Set<String> = []

    private var transactionListener: Task<Void, Error>?

    init() {
        transactionListener = listenForTransactions()
    }

    deinit { transactionListener?.cancel() }

    /// 从 App Store 加载商品列表
    func loadProducts(productIDs: [String]) async throws {
        products = try await Product.products(for: productIDs)
    }

    /// 发起购买
    func purchase(_ product: Product) async throws -> Bool {
        let result = try await product.purchase()
        switch result {
        case .success(let verification):
            let transaction = try checkVerified(verification)
            await updatePurchasedProducts()
            await transaction.finish()
            return true
        case .userCancelled, .pending:
            return false
        @unknown default:
            return false
        }
    }

    /// 恢复购买
    func restorePurchases() async throws {
        try await AppStore.sync()
        await updatePurchasedProducts()
    }

    private func listenForTransactions() -> Task<Void, Error> {
        Task.detached {
            for await result in Transaction.updates {
                if case .verified(let transaction) = result {
                    await self.updatePurchasedProducts()
                    await transaction.finish()
                }
            }
        }
    }

    private func updatePurchasedProducts() async {
        for await result in Transaction.currentEntitlements {
            if case .verified(let transaction) = result,
               transaction.revocationDate == nil {
                purchasedProductIDs.insert(transaction.productID)
            }
        }
    }

    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified: throw StoreError.failedVerification
        case .verified(let safe): return safe
        }
    }
}
'''

TEMPLATE_IAP_KOTLIN = '''// ── Billing Manager (Play Billing Library 6+) ────────────────────
// 合规要点：所有数字商品必须通过 Play Billing，不得引导外部支付
// 参考：Google Play 结算政策
// build.gradle 依赖：implementation "com.android.billingclient:billing-ktx:6.2.1"

import android.app.Activity
import com.android.billingclient.api.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class BillingManager(
    private val activity: Activity,
    private val onPurchaseSuccess: (Purchase) -> Unit,
    private val onPurchaseFailed: (Int, String) -> Unit
) : PurchasesUpdatedListener {

    private lateinit var billingClient: BillingClient

    fun initialize() {
        billingClient = BillingClient.newBuilder(activity)
            .setListener(this)
            .enablePendingPurchases()
            .build()
        connectBillingService()
    }

    private fun connectBillingService() {
        billingClient.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                    // 连接成功，可以查询商品
                }
            }
            override fun onBillingServiceDisconnected() {
                connectBillingService() // 自动重连
            }
        })
    }

    suspend fun queryProducts(productIds: List<String>): List<ProductDetails> {
        val params = QueryProductDetailsParams.newBuilder()
            .setProductList(productIds.map {
                QueryProductDetailsParams.Product.newBuilder()
                    .setProductId(it)
                    .setProductType(BillingClient.ProductType.INAPP)
                    .build()
            }).build()

        return withContext(Dispatchers.IO) {
            val result = billingClient.queryProductDetails(params)
            result.productDetailsList ?: emptyList()
        }
    }

    fun launchPurchaseFlow(productDetails: ProductDetails) {
        val params = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(
                listOf(BillingFlowParams.ProductDetailsParams.newBuilder()
                    .setProductDetails(productDetails)
                    .build())
            ).build()
        billingClient.launchBillingFlow(activity, params)
    }

    override fun onPurchasesUpdated(result: BillingResult, purchases: List<Purchase>?) {
        if (result.responseCode == BillingClient.BillingResponseCode.OK && purchases != null) {
            purchases.forEach { purchase ->
                if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
                    // ⚠️ 必须在服务端验证 purchaseToken，再 acknowledge
                    verifyOnServerAndAcknowledge(purchase)
                }
            }
        } else {
            onPurchaseFailed(result.responseCode, result.debugMessage)
        }
    }

    private fun verifyOnServerAndAcknowledge(purchase: Purchase) {
        CoroutineScope(Dispatchers.IO).launch {
            // TODO: 调用你的后端 API 验证 purchaseToken
            // POST /api/verify-purchase { purchaseToken: purchase.purchaseToken }
            val verified = true // 替换为真实验证结果

            if (verified && !purchase.isAcknowledged) {
                val ackParams = AcknowledgePurchaseParams.newBuilder()
                    .setPurchaseToken(purchase.purchaseToken)
                    .build()
                billingClient.acknowledgePurchase(ackParams) { ackResult ->
                    if (ackResult.responseCode == BillingClient.BillingResponseCode.OK) {
                        onPurchaseSuccess(purchase)
                    }
                }
            }
        }
    }

    fun release() { billingClient.endConnection() }
}
'''

TEMPLATE_IAP_UNITY = '''// ── Unity IAP Manager (跨平台：StoreKit + Play Billing) ──────────
// 合规要点：Unity IAP 底层自动对接 StoreKit (iOS) 和 Play Billing (Android)
// 依赖：Window > Package Manager > Unity IAP (com.unity.purchasing)
// 参考：App Store 3.1.1 / Google Play 结算政策

using UnityEngine;
using UnityEngine.Purchasing;
using UnityEngine.Purchasing.Extension;
using System;

public class IAPManager : MonoBehaviour, IDetailedStoreListener
{
    public static IAPManager Instance { get; private set; }

    private static IStoreController _storeController;
    private static IExtensionProvider _storeExtensionProvider;

    // 在 Inspector 或代码中填入你的商品 ID
    [Header("商品 ID（与 App Store Connect / Play Console 一致）")]
    public string consumableProductId  = "com.yourcompany.yourapp.coins100";
    public string subscriptionProductId = "com.yourcompany.yourapp.premium_monthly";

    public event Action<string> OnPurchaseSuccess;
    public event Action<string, string> OnPurchaseFailed;

    void Awake()
    {
        if (Instance != null) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);
        InitializePurchasing();
    }

    void InitializePurchasing()
    {
        var builder = ConfigurationBuilder.Instance(StandardPurchasingModule.Instance());
        builder.AddProduct(consumableProductId,  ProductType.Consumable);
        builder.AddProduct(subscriptionProductId, ProductType.Subscription);
        UnityPurchasing.Initialize(this, builder);
    }

    public void BuyConsumable()  => BuyProductID(consumableProductId);
    public void BuySubscription() => BuyProductID(subscriptionProductId);

    void BuyProductID(string productId)
    {
        if (_storeController == null) { Debug.LogError("IAP 未初始化"); return; }
        _storeController.InitiatePurchase(productId);
    }

    public void RestorePurchases()
    {
#if UNITY_IOS
        var apple = _storeExtensionProvider.GetExtension<IAppleExtensions>();
        apple.RestoreTransactions(result => {
            Debug.Log(result ? "恢复购买成功" : "恢复购买失败");
        });
#endif
    }

    // ── IDetailedStoreListener 回调 ─────────────────────────────

    public void OnInitialized(IStoreController controller, IExtensionProvider extensions)
    {
        _storeController = controller;
        _storeExtensionProvider = extensions;
        Debug.Log("Unity IAP 初始化成功");
    }

    public PurchaseProcessingResult ProcessPurchase(PurchaseEventArgs args)
    {
        // ⚠️ 必须在服务端验证收据，验证成功后再调用 ConfirmPendingPurchase
        StartCoroutine(ValidateOnServer(args));
        return PurchaseProcessingResult.Pending;
    }

    System.Collections.IEnumerator ValidateOnServer(PurchaseEventArgs args)
    {
        // TODO: 将 args.purchasedProduct.receipt 发送到你的后端验证
        // 验证通过后：
        _storeController.ConfirmPendingPurchase(args.purchasedProduct);
        OnPurchaseSuccess?.Invoke(args.purchasedProduct.definition.id);
        yield return null;
    }

    public void OnInitializeFailed(InitializationFailureReason error, string message) =>
        Debug.LogError($"IAP 初始化失败: {error} - {message}");

    public void OnPurchaseFailed(Product product, PurchaseFailureDescription failureDescription)
    {
        OnPurchaseFailed?.Invoke(product.definition.id, failureDescription.message);
        Debug.LogWarning($"购买失败: {product.definition.id} - {failureDescription.reason}");
    }
}
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ATT — App Tracking Transparency（仅 iOS）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMPLATE_ATT_SWIFT = '''// ── ATT Manager (App Tracking Transparency) ──────────────────────
// 合规要点：iOS 14.5+ 使用 IDFA 或跨 App 追踪前必须请求用户授权
// 儿童 App 完全禁止使用，min_user_age < 13 时不得调用此模块
// Info.plist 需添加：NSUserTrackingUsageDescription
// 参考：App Store Guideline 5.1.2

import AppTrackingTransparency
import AdSupport

class ATTManager {
    static func requestAuthorization(minUserAge: Int, completion: @escaping (Bool) -> Void) {
        // ⚠️ 儿童 App 禁止请求追踪授权
        guard minUserAge >= 13 else {
            completion(false)
            return
        }

        if #available(iOS 14.5, *) {
            ATTrackingManager.requestTrackingAuthorization { status in
                DispatchQueue.main.async {
                    completion(status == .authorized)
                }
            }
        } else {
            completion(true) // iOS 14.5 以下默认允许
        }
    }

    /// 获取 IDFA（仅在授权后调用）
    static var idfa: String? {
        if #available(iOS 14.5, *) {
            guard ATTrackingManager.trackingAuthorizationStatus == .authorized else { return nil }
        }
        return ASIdentifierManager.shared().advertisingIdentifier.uuidString
    }
}

// 在 AppDelegate 或首页 viewDidAppear 中调用（不要在 viewDidLoad 中调用）：
// ATTManager.requestAuthorization(minUserAge: 16) { granted in
//     if granted { /* 启用个性化广告 */ }
// }
'''

TEMPLATE_ATT_UNITY = '''// ── ATT Request (Unity — iOS 专属) ───────────────────────────────
// Unity 包：com.unity.advertisement.ios.support 或 Apple.GameKit
// 也可直接使用 Unity Ads SDK 内置的 ATT 请求功能
// Info.plist 需添加：NSUserTrackingUsageDescription
// 参考：App Store Guideline 5.1.2

using UnityEngine;
#if UNITY_IOS
using Unity.Advertisement.IosSupport;
#endif

public class ATTHandler : MonoBehaviour
{
    [Header("最低用户年龄（< 13 时禁止请求 ATT）")]
    public int minUserAge = 16;

    void Start()
    {
        RequestATTIfNeeded();
    }

    public void RequestATTIfNeeded()
    {
        // 儿童 App 禁止
        if (minUserAge < 13)
        {
            Debug.Log("儿童 App 不得请求 ATT");
            return;
        }

#if UNITY_IOS
        if (ATTrackingStatusBinding.GetAuthorizationTrackingStatus() ==
            ATTrackingStatusBinding.AuthorizationTrackingStatus.NOT_DETERMINED)
        {
            ATTrackingStatusBinding.RequestAuthorizationTracking(OnATTResult);
        }
#endif
    }

#if UNITY_IOS
    void OnATTResult(ATTrackingStatusBinding.AuthorizationTrackingStatus status)
    {
        if (status == ATTrackingStatusBinding.AuthorizationTrackingStatus.AUTHORIZED)
        {
            Debug.Log("用户授权追踪，可启用个性化广告");
        }
        else
        {
            Debug.Log("用户拒绝追踪，使用非个性化广告");
        }
    }
#endif
}
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 账户删除
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMPLATE_ACCOUNT_DELETE_SWIFT = '''// ── Account Deletion Flow (iOS) ──────────────────────────────────
// 合规要点：设置页必须提供"删除账户"入口（不是注销），彻底删除所有数据
// 参考：App Store Guideline 5.1.1(v)，2022年6月起强制

import SwiftUI

struct AccountDeletionView: View {
    @State private var showConfirmation = false
    @State private var isDeleting = false
    @State private var errorMessage: String?

    var body: some View {
        VStack(spacing: 20) {
            Text("删除账户")
                .font(.title2).bold()

            Text("删除账户将永久移除您的所有数据，包括：\\n• 个人信息\\n• 游戏进度\\n• 购买记录（虚拟物品）\\n\\n此操作不可撤销。")
                .foregroundColor(.secondary)
                .multilineTextAlignment(.leading)

            if let error = errorMessage {
                Text(error).foregroundColor(.red).font(.caption)
            }

            Button(role: .destructive) {
                showConfirmation = true
            } label: {
                if isDeleting {
                    ProgressView().tint(.white)
                } else {
                    Text("删除我的账户")
                }
            }
            .disabled(isDeleting)
        }
        .padding()
        .confirmationDialog("确认删除账户？", isPresented: $showConfirmation, titleVisibility: .visible) {
            Button("永久删除", role: .destructive) { deleteAccount() }
            Button("取消", role: .cancel) {}
        } message: {
            Text("此操作无法撤销，所有数据将在 30 天内彻底删除。")
        }
    }

    private func deleteAccount() {
        isDeleting = true
        Task {
            do {
                try await AccountService.deleteAccount()
                // 退出登录，跳转到首页
            } catch {
                errorMessage = "删除失败，请稍后重试"
                isDeleting = false
            }
        }
    }
}

class AccountService {
    static func deleteAccount() async throws {
        // 调用后端 API
        // DELETE /api/v1/user/account
        // 后端须：删除所有 PII，撤销第三方授权，保留法务必要数据
    }
}
'''

TEMPLATE_ACCOUNT_DELETE_KOTLIN = '''// ── Account Deletion Flow (Android) ──────────────────────────────
// 合规要点：App 内入口 + 必须提供网页版删除链接（在 Play Console 填写 URL）
// 参考：Google Play 账户删除政策，2024年5月起强制

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import retrofit2.http.DELETE

class AccountDeletionActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 显示二次确认对话框
        AlertDialog.Builder(this)
            .setTitle("删除账户")
            .setMessage("删除账户将永久移除您的所有数据。\\n此操作不可撤销，数据将在 30 天内彻底删除。")
            .setPositiveButton("确认删除") { _, _ -> performDeletion() }
            .setNegativeButton("取消", null)
            .show()
    }

    private fun performDeletion() {
        lifecycleScope.launch {
            try {
                AccountRepository.deleteAccount()
                Toast.makeText(this@AccountDeletionActivity, "账户已提交删除申请", Toast.LENGTH_LONG).show()
                // 退出登录，返回首页
                finishAffinity()
            } catch (e: Exception) {
                Toast.makeText(this@AccountDeletionActivity, "删除失败，请稍后重试", Toast.LENGTH_SHORT).show()
            }
        }
    }
}

// ── 在设置页 Settings Fragment 中添加删除入口 ─────────────────────

class SettingsFragment : PreferenceFragmentCompat() {
    override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
        // ...
        findPreference<Preference>("delete_account")?.setOnPreferenceClickListener {
            startActivity(Intent(requireContext(), AccountDeletionActivity::class.java))
            true
        }

        // 提供网页版删除链接（供卸载后使用，在 Play Console 也须填写此 URL）
        findPreference<Preference>("delete_account_web")?.setOnPreferenceClickListener {
            val uri = Uri.parse("https://yourcompany.com/account/delete")
            startActivity(Intent(Intent.ACTION_VIEW, uri))
            true
        }
    }
}

interface AccountApiService {
    @DELETE("api/v1/user/account")
    suspend fun deleteAccount()
}
'''

TEMPLATE_ACCOUNT_DELETE_UNITY = '''// ── Account Deletion Flow (Unity 跨平台) ─────────────────────────
// iOS：设置页内入口即可
// Android：还需提供网页版删除链接（在 Play Console 填写）
// 参考：App Store 5.1.1(v) / Google Play 账户删除政策

using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using UnityEngine.Networking;

public class AccountDeletionUI : MonoBehaviour
{
    [Header("UI 引用")]
    public GameObject confirmPanel;
    public Button deleteButton;
    public Button cancelButton;

    [Header("网页版删除页 URL（Android Play Console 须填写此 URL）")]
    public string webDeletionUrl = "https://yourcompany.com/account/delete";

    void Start()
    {
        confirmPanel.SetActive(false);
        deleteButton.onClick.AddListener(OnDeleteConfirmed);
        cancelButton.onClick.AddListener(() => confirmPanel.SetActive(false));
    }

    /// 从设置菜单按钮调用此方法
    public void ShowDeleteConfirmation()
    {
        confirmPanel.SetActive(true);
    }

    /// Android 专用：打开网页版删除页
    public void OpenWebDeletion()
    {
        Application.OpenURL(webDeletionUrl);
    }

    void OnDeleteConfirmed()
    {
        deleteButton.interactable = false;
        StartCoroutine(DeleteAccountRequest());
    }

    IEnumerator DeleteAccountRequest()
    {
        string authToken = PlayerPrefs.GetString("auth_token");
        string apiUrl = "https://yourcompany.com/api/v1/user/account";

        using (var request = UnityWebRequest.Delete(apiUrl))
        {
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                // 清除本地数据并退出登录
                PlayerPrefs.DeleteAll();
                Debug.Log("账户删除申请成功");
                // 跳转到登录页
            }
            else
            {
                Debug.LogError($"账户删除失败: {request.error}");
                deleteButton.interactable = true;
            }
        }
    }
}
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Sign in with Apple（仅 iOS 强制）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMPLATE_SIGN_IN_APPLE_SWIFT = '''// ── Sign in with Apple ────────────────────────────────────────────
// 合规要点：提供任何第三方登录时，必须同时提供 Sign in with Apple
// 参考：App Store Guideline 4.8
// Xcode：Signing & Capabilities → + Sign In with Apple

import AuthenticationServices
import SwiftUI

struct SignInWithAppleButton_: View {
    var body: some View {
        SignInWithAppleButton(.signIn) { request in
            request.requestedScopes = [.email, .fullName]
        } onCompletion: { result in
            switch result {
            case .success(let auth):
                if let credential = auth.credential as? ASAuthorizationAppleIDCredential {
                    handleAppleCredential(credential)
                }
            case .failure(let error):
                print("Sign in with Apple 失败: \\(error)")
            }
        }
        .signInWithAppleButtonStyle(.black)
        .frame(height: 44)
    }

    private func handleAppleCredential(_ credential: ASAuthorizationAppleIDCredential) {
        let userID = credential.user                              // 稳定用户标识
        let identityToken = credential.identityToken             // JWT，须发送到后端验证
        let email = credential.email                             // 首次登录才有，之后为 nil
        let fullName = credential.fullName

        // 发送到后端验证 identityToken（用 Apple 公钥解码 JWT）
        // POST /api/v1/auth/apple { identity_token, user_id, email, name }
    }
}
'''

TEMPLATE_SIGN_IN_APPLE_UNITY = '''// ── Sign in with Apple (Unity) ────────────────────────────────────
// 插件：Apple.GameKit (com.apple.unityplugin.gamekit) 或
//       ByoungminKim/apple-signin-unity (开源)
// 参考：App Store Guideline 4.8（有第三方登录时强制）

using UnityEngine;
#if UNITY_IOS
using AppleAuth;
using AppleAuth.Native;
using AppleAuth.Enums;
using AppleAuth.Extensions;
using AppleAuth.Interfaces;
#endif

public class AppleSignInManager : MonoBehaviour
{
#if UNITY_IOS
    private IAppleAuthManager _appleAuthManager;

    void Start()
    {
        if (AppleAuthManager.IsCurrentPlatformSupported)
        {
            var deserializer = new PayloadDeserializer();
            _appleAuthManager = new AppleAuthManager(deserializer);
        }
    }

    void Update()
    {
        _appleAuthManager?.Update();
    }

    public void SignInWithApple()
    {
        var loginArgs = new AppleAuthLoginArgs(LoginOptions.IncludeEmail | LoginOptions.IncludeFullName);
        _appleAuthManager.LoginWithAppleId(loginArgs, OnSignInSuccess, OnSignInFailed);
    }

    void OnSignInSuccess(ICredential credential)
    {
        if (credential is IAppleIDCredential appleCredential)
        {
            var identityToken = System.Text.Encoding.UTF8.GetString(appleCredential.IdentityToken);
            var userID = appleCredential.User;
            var email = appleCredential.Email; // 首次登录才有

            // 发送到后端验证
            // POST /api/v1/auth/apple { identity_token, user_id, email }
            Debug.Log($"Apple 登录成功，userID: {userID}");
        }
    }

    void OnSignInFailed(IAppleError error)
    {
        Debug.LogError($"Apple 登录失败: {error.LocalizedDescription}");
    }
#endif
}
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 儿童 App / 家长门控
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMPLATE_KIDS_SWIFT = '''// ── Parental Gate (Apple 要求的家长门控) ─────────────────────────
// 合规要点：儿童 App 中所有外部链接/付费内容前必须通过家长门控
// Apple 要求：随机数学题或同等难度的复杂操作（不能是简单点击）
// 参考：App Store Guideline 1.3

import SwiftUI

struct ParentalGateView: View {
    let onSuccess: () -> Void
    let onCancel: () -> Void

    @State private var num1 = Int.random(in: 10...99)
    @State private var num2 = Int.random(in: 10...99)
    @State private var userAnswer = ""
    @State private var isWrong = false

    private var correctAnswer: Int { num1 + num2 }

    var body: some View {
        VStack(spacing: 20) {
            Text("家长验证")
                .font(.title2).bold()

            Text("请计算以下题目（需要家长帮助）：")
                .foregroundColor(.secondary)

            Text("\\(num1) + \\(num2) = ?")
                .font(.system(size: 36, weight: .bold, design: .rounded))
                .foregroundColor(.primary)

            TextField("输入答案", text: $userAnswer)
                .keyboardType(.numberPad)
                .textFieldStyle(.roundedBorder)
                .frame(maxWidth: 120)
                .multilineTextAlignment(.center)

            if isWrong {
                Text("答案错误，请重试")
                    .foregroundColor(.red).font(.caption)
            }

            HStack(spacing: 20) {
                Button("取消") { onCancel() }
                    .foregroundColor(.secondary)

                Button("确认") {
                    if Int(userAnswer) == correctAnswer {
                        onSuccess()
                    } else {
                        isWrong = true
                        // 重新生成题目
                        num1 = Int.random(in: 10...99)
                        num2 = Int.random(in: 10...99)
                        userAnswer = ""
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(userAnswer.isEmpty)
            }
        }
        .padding()
    }
}

// 使用示例：在外部链接、社交功能、付费内容入口前展示
// ParentalGateView { openExternalLink() } onCancel: {}
'''

TEMPLATE_KIDS_UNITY = '''// ── Parental Gate (Unity 跨平台) ─────────────────────────────────
// iOS：Apple 要求随机数学题
// Android：Google Play 家庭政策要求类似的家长验证
// 参考：App Store 1.3 / Google Play 家庭政策

using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;

public class ParentalGate : MonoBehaviour
{
    [Header("UI 引用")]
    public GameObject gatePanel;
    public TMP_Text questionText;
    public TMP_InputField answerInput;
    public TMP_Text errorText;

    private int _correctAnswer;
    private Action _onSuccess;
    private Action _onCancel;

    /// 在外部链接 / 社交功能 / 付费内容入口前调用
    public void Show(Action onSuccess, Action onCancel = null)
    {
        _onSuccess = onSuccess;
        _onCancel = onCancel;
        GenerateQuestion();
        gatePanel.SetActive(true);
        answerInput.text = "";
        errorText.gameObject.SetActive(false);
    }

    void GenerateQuestion()
    {
        // Apple 要求：不能是简单点击，须为随机数学计算题
        int a = UnityEngine.Random.Range(10, 100);
        int b = UnityEngine.Random.Range(10, 100);
        _correctAnswer = a + b;
        questionText.text = $"{a} + {b} = ?";
    }

    public void OnConfirm()
    {
        if (int.TryParse(answerInput.text, out int userAnswer) && userAnswer == _correctAnswer)
        {
            gatePanel.SetActive(false);
            _onSuccess?.Invoke();
        }
        else
        {
            errorText.text = "答案错误，请重试";
            errorText.gameObject.SetActive(true);
            GenerateQuestion();
            answerInput.text = "";
        }
    }

    public void OnCancel()
    {
        gatePanel.SetActive(false);
        _onCancel?.Invoke();
    }
}

// ── 广告 SDK 儿童模式配置 ─────────────────────────────────────────
// 在游戏初始化时调用，13 岁以下用户必须设置

public class AdsPrivacyConfig : MonoBehaviour
{
    public bool isChildDirected = true; // 根据实际用户年龄动态设置

    void Awake()
    {
        if (isChildDirected)
        {
            ConfigureChildDirectedAds();
        }
    }

    void ConfigureChildDirectedAds()
    {
        // Unity Ads
        // MetaData metaData = new MetaData("privacy");
        // metaData.Set("user-non-behavioral", "true");
        // Advertisement.SetMetaData(metaData);

        // Google AdMob (via Unity plugin)
        // RequestConfiguration config = new RequestConfiguration.Builder()
        //     .SetTagForChildDirectedTreatment(TagForChildDirectedTreatment.True)
        //     .build();
        // MobileAds.SetRequestConfiguration(config);

        Debug.Log("已启用儿童广告合规模式（非个性化广告）");
    }
}
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 隐私政策入口
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMPLATE_PRIVACY_UNITY = '''// ── Privacy Policy & Terms UI (Unity 跨平台) ──────────────────────
// 合规要点：iOS + Android 均要求 App 内提供隐私政策入口
// Android 还需在 Play Console 填写公开 URL
// 参考：App Store 5.1 / Google Play 用户数据政策

using UnityEngine;
using UnityEngine.UI;

public class PrivacyPolicyUI : MonoBehaviour
{
    [Header("URL 配置（与 App Store Connect / Play Console 保持一致）")]
    public string privacyPolicyUrl = "https://yourcompany.com/privacy";
    public string termsOfServiceUrl = "https://yourcompany.com/terms";

    // 首次启动时展示同意弹窗
    public GameObject consentPanel;
    public Toggle agreeToggle;
    public Button continueButton;

    void Start()
    {
        bool hasConsented = PlayerPrefs.GetInt("privacy_consented", 0) == 1;
        if (!hasConsented && consentPanel != null)
        {
            consentPanel.SetActive(true);
            continueButton.interactable = false;
            agreeToggle.onValueChanged.AddListener(isOn => continueButton.interactable = isOn);
        }
    }

    public void OnConsentConfirmed()
    {
        PlayerPrefs.SetInt("privacy_consented", 1);
        PlayerPrefs.SetString("privacy_consent_date", System.DateTime.UtcNow.ToString("o"));
        PlayerPrefs.Save();
        consentPanel.SetActive(false);
    }

    public void OpenPrivacyPolicy() => Application.OpenURL(privacyPolicyUrl);
    public void OpenTermsOfService() => Application.OpenURL(termsOfServiceUrl);
}
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 模板目录（feature → platform → 代码）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMPLATE_CATALOG = {
    "iap": {
        "title": "应用内购买",
        "guideline": "App Store 3.1.1 / Google Play 结算政策",
        "ios": {
            "filename": "IAPManager.swift",
            "language": "swift",
            "code": TEMPLATE_IAP_SWIFT,
        },
        "android": {
            "filename": "BillingManager.kt",
            "language": "kotlin",
            "code": TEMPLATE_IAP_KOTLIN,
        },
        "unity": {
            "filename": "IAPManager.cs",
            "language": "csharp",
            "code": TEMPLATE_IAP_UNITY,
        },
    },
    "att": {
        "title": "App Tracking Transparency（ATT）",
        "guideline": "App Store Guideline 5.1.2（iOS 14.5+）",
        "ios": {
            "filename": "ATTManager.swift",
            "language": "swift",
            "code": TEMPLATE_ATT_SWIFT,
        },
        "android": {
            "filename": None,
            "language": None,
            "code": "// Android 无对应要求。\n// 如使用 Advertising ID，参考 Privacy Sandbox 相关文档。",
        },
        "unity": {
            "filename": "ATTHandler.cs",
            "language": "csharp",
            "code": TEMPLATE_ATT_UNITY,
        },
    },
    "account_deletion": {
        "title": "账户删除",
        "guideline": "App Store 5.1.1(v) / Google Play 账户删除政策",
        "ios": {
            "filename": "AccountDeletionView.swift",
            "language": "swift",
            "code": TEMPLATE_ACCOUNT_DELETE_SWIFT,
        },
        "android": {
            "filename": "AccountDeletionActivity.kt",
            "language": "kotlin",
            "code": TEMPLATE_ACCOUNT_DELETE_KOTLIN,
        },
        "unity": {
            "filename": "AccountDeletionUI.cs",
            "language": "csharp",
            "code": TEMPLATE_ACCOUNT_DELETE_UNITY,
        },
    },
    "social_login": {
        "title": "Sign in with Apple（有第三方登录时强制）",
        "guideline": "App Store Guideline 4.8",
        "ios": {
            "filename": "AppleSignIn.swift",
            "language": "swift",
            "code": TEMPLATE_SIGN_IN_APPLE_SWIFT,
        },
        "android": {
            "filename": None,
            "language": None,
            "code": "// Android 无 Sign in with Apple 要求。\n// 推荐提供 Google Sign-In 作为对等方案。",
        },
        "unity": {
            "filename": "AppleSignInManager.cs",
            "language": "csharp",
            "code": TEMPLATE_SIGN_IN_APPLE_UNITY,
        },
    },
    "kids": {
        "title": "儿童保护 / 家长门控",
        "guideline": "App Store 1.3 / Google Play 家庭政策",
        "ios": {
            "filename": "ParentalGateView.swift",
            "language": "swift",
            "code": TEMPLATE_KIDS_SWIFT,
        },
        "android": {
            "filename": "ParentalGate.kt",
            "language": "kotlin",
            "code": "// Android：使用 Google Play 家庭政策批准的 SDK\n// 参考：https://support.google.com/googleplay/android-developer/answer/9893335",
        },
        "unity": {
            "filename": "ParentalGate.cs",
            "language": "csharp",
            "code": TEMPLATE_KIDS_UNITY,
        },
    },
    "privacy": {
        "title": "隐私政策入口",
        "guideline": "App Store 5.1 / Google Play 用户数据政策",
        "ios": {
            "filename": "PrivacyPolicyView.swift",
            "language": "swift",
            "code": '// 在 Settings 页添加按钮：\n// Link("隐私政策", destination: URL(string: "https://yourcompany.com/privacy")!)',
        },
        "android": {
            "filename": "PrivacyPolicyPreference.kt",
            "language": "kotlin",
            "code": '// 在 PreferenceFragment 中添加：\n// <Preference android:key="privacy_policy"\n//     android:title="隐私政策"\n//     android:summary="点击查看我们的隐私政策" />',
        },
        "unity": {
            "filename": "PrivacyPolicyUI.cs",
            "language": "csharp",
            "code": TEMPLATE_PRIVACY_UNITY,
        },
    },
}

# ── 公开接口 ─────────────────────────────────────────────────────────────────

def generate_templates(
    features: List[str],
    platforms: List[str],
    min_user_age: int = 18,
) -> Dict[str, Any]:
    """
    根据 App 功能和目标平台，生成对应的合规代码模板。

    参数：
      features    - 功能列表，如 ['iap', 'att', 'kids', 'social_login', 'privacy']
      platforms   - 平台列表，如 ['ios', 'android', 'unity']
      min_user_age - 最小用户年龄，影响儿童相关模板是否生成

    返回：
      结构化结果，包含每个 feature 在每个 platform 上的代码模板
    """
    # 自动推断：有 min_user_age < 13 就加入 kids
    effective_features = list(features)
    if min_user_age < 13 and "kids" not in effective_features:
        effective_features.append("kids")
    # 始终建议包含 privacy 和 account_deletion
    for auto in ("privacy", "account_deletion"):
        if auto not in effective_features:
            effective_features.append(auto)

    result = {
        "meta": {
            "features": effective_features,
            "platforms": platforms,
            "min_user_age": min_user_age,
            "kids_mode": min_user_age < 13,
            "templates_count": 0,
        },
        "templates": [],
        "project_checklist": [],
        "warnings": [],
    }

    for feature in effective_features:
        catalog_entry = TEMPLATE_CATALOG.get(feature)
        if not catalog_entry:
            continue

        template_entry = {
            "feature": feature,
            "title": catalog_entry["title"],
            "guideline": catalog_entry["guideline"],
            "files": [],
        }

        for platform in platforms:
            platform_data = catalog_entry.get(platform)
            if not platform_data:
                continue

            if platform_data.get("filename"):
                template_entry["files"].append({
                    "platform": platform,
                    "filename": platform_data["filename"],
                    "language": platform_data["language"],
                    "code": platform_data["code"],
                })
                result["meta"]["templates_count"] += 1

        result["templates"].append(template_entry)

    # 生成项目检查清单
    result["project_checklist"] = _build_checklist(effective_features, platforms, min_user_age)

    # 特殊警告
    if min_user_age < 13 and "att" in effective_features:
        result["warnings"].append(
            "⚠️ 儿童 App（min_user_age < 13）禁止使用 ATT，ATT 模板已生成但不应调用"
        )
    if "social_login" in effective_features and "ios" in platforms:
        result["warnings"].append(
            "⚠️ 提供第三方登录时，iOS 必须同时集成 Sign in with Apple（已包含模板）"
        )

    return result


def _build_checklist(features: List[str], platforms: List[str], min_age: int) -> List[Dict]:
    items = []

    if "iap" in features:
        if "ios" in platforms or "unity" in platforms:
            items.append({"platform": "iOS", "item": "App Store Connect → 填写银行账户信息", "type": "platform_config"})
            items.append({"platform": "iOS", "item": "在 App Store Connect 创建 IAP 商品（Product ID 须与代码一致）", "type": "platform_config"})
        if "android" in platforms or "unity" in platforms:
            items.append({"platform": "Android", "item": "Play Console → 创建应用内商品或订阅", "type": "platform_config"})
            items.append({"platform": "Android", "item": "配置 Google Play 结算后端验证（Developer API）", "type": "backend"})

    if "att" in features and ("ios" in platforms or "unity" in platforms):
        items.append({"platform": "iOS", "item": "Info.plist 添加 NSUserTrackingUsageDescription", "type": "config"})

    if "account_deletion" in features:
        if "ios" in platforms or "unity" in platforms:
            items.append({"platform": "iOS", "item": "后端实现 DELETE /api/v1/user/account，30天内彻底删除数据", "type": "backend"})
        if "android" in platforms or "unity" in platforms:
            items.append({"platform": "Android", "item": "Play Console → 应用内容 → 账户删除 → 填写网页版删除 URL", "type": "platform_config"})

    if "social_login" in features and ("ios" in platforms or "unity" in platforms):
        items.append({"platform": "iOS", "item": "Xcode → Signing & Capabilities → 添加 Sign In with Apple", "type": "config"})
        items.append({"platform": "iOS", "item": "后端实现 Apple identity_token 验证（使用 Apple 公钥解码 JWT）", "type": "backend"})

    items.append({"platform": "iOS", "item": "App Store Connect → 应用隐私 → 填写隐私营养标签", "type": "platform_config"})
    items.append({"platform": "Android", "item": "Play Console → 应用内容 → 数据安全 → 填写数据安全表单", "type": "platform_config"})
    items.append({"platform": "Android", "item": "Play Console → 应用内容 → 内容分级 → 完成 IARC 问卷", "type": "platform_config"})

    if min_age < 13:
        items.append({"platform": "iOS", "item": "仅使用 Apple Families 批准的第三方 SDK（广告/分析）", "type": "review"})
        items.append({"platform": "Android", "item": "Play Console → 应用内容 → 目标受众 → 选择儿童年龄段", "type": "platform_config"})

    return items
